#!/usr/bin/env python3
"""
ClawHub Skill Publishing Script
Automates the complete workflow for publishing skills to ClawHub
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# Notion configuration
NOTION_API_KEY_PATH = Path.home() / ".config/notion/api_key"
PASSWORD_DB_ID = "26c29e15-c2b5-810e-97b8-dcd41413d230"
TASKS_DB_ID = "b1d94366-de4e-46c5-959f-3d73611d3379"

class SkillPublisher:
    def __init__(self, skill_path, dry_run=False):
        self.skill_path = Path(skill_path).resolve()
        self.dry_run = dry_run
        self.notion_api_key = self._load_notion_key()
        
    def _load_notion_key(self):
        """Load Notion API key"""
        try:
            with open(NOTION_API_KEY_PATH, 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            print("❌ Notion API key not found")
            sys.exit(1)
    
    def _get_github_token(self):
        """Retrieve GitHub token from Notion Password Manager"""
        import requests
        
        url = f"https://api.notion.com/v1/databases/{PASSWORD_DB_ID}/query"
        headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        payload = {
            "filter": {
                "property": "Website Name",
                "title": {"contains": "GitHub Personal Access Token"}
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                password_prop = results[0]["properties"]["Password"]["rich_text"]
                if password_prop:
                    return password_prop[0]["text"]["content"]
        
        print("❌ GitHub token not found in Notion")
        sys.exit(1)
    
    def _run_command(self, cmd, cwd=None, capture=False):
        """Run shell command"""
        if self.dry_run:
            print(f"[DRY RUN] Would execute: {' '.join(cmd)}")
            return True, ""
        
        try:
            if capture:
                result = subprocess.run(
                    cmd,
                    cwd=cwd or self.skill_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                return True, result.stdout.strip()
            else:
                result = subprocess.run(
                    cmd,
                    cwd=cwd or self.skill_path,
                    check=True
                )
                return True, ""
        except subprocess.CalledProcessError as e:
            return False, str(e)
    
    def update_version_in_readme(self, version):
        """Update version badge in README"""
        readme_path = self.skill_path / "README.md"
        if not readme_path.exists():
            return
        
        with open(readme_path, 'r') as f:
            content = f.read()
        
        # Update version badge
        import re
        content = re.sub(
            r'badge/version-[\d\.]+',
            f'badge/version-{version}',
            content
        )
        
        # Update version mention in first paragraph
        content = re.sub(
            r'\*\*v[\d\.]+\*\*',
            f'**v{version}**',
            content,
            count=1
        )
        
        if not self.dry_run:
            with open(readme_path, 'w') as f:
                f.write(content)
        
        print(f"✓ Updated version in README.md to {version}")
    
    def git_commit_and_push(self, version, changelog):
        """Stage, commit, and push to GitHub"""
        print("\n📦 Git Operations:")
        
        # Stage all changes
        success, _ = self._run_command(['git', 'add', '-A'])
        if not success:
            print("❌ Failed to stage changes")
            return False
        print("✓ Staged all changes")
        
        # Create commit message
        commit_msg = f"Release v{version}\n\n{changelog}"
        
        # Commit
        success, _ = self._run_command(['git', 'commit', '-m', commit_msg])
        if not success:
            print("⚠️  No changes to commit (or commit failed)")
        else:
            print(f"✓ Committed: v{version}")
        
        # Get GitHub token and configure remote
        github_token = self._get_github_token()
        
        # Get current remote URL
        success, remote_url = self._run_command(
            ['git', 'remote', 'get-url', 'origin'],
            capture=True
        )
        
        if not success:
            print("❌ Failed to get remote URL")
            return False
        
        # Extract repo path from URL
        import re
        repo_match = re.search(r'github\.com[:/](.+?)(?:\.git)?$', remote_url)
        if not repo_match:
            print("❌ Invalid GitHub remote URL")
            return False
        
        repo_path = repo_match.group(1).replace('.git', '')
        authenticated_url = f"https://{github_token}@github.com/{repo_path}.git"
        
        # Update remote URL temporarily
        success, _ = self._run_command(
            ['git', 'remote', 'set-url', 'origin', authenticated_url]
        )
        if not success:
            print("❌ Failed to set authenticated remote")
            return False
        
        # Push
        success, _ = self._run_command(['git', 'push', 'origin', 'main'])
        if not success:
            print("❌ Failed to push to GitHub")
            return False
        
        print("✓ Pushed to GitHub")
        return True
    
    def publish_to_clawhub(self, version, changelog, tags="latest"):
        """Publish to ClawHub registry"""
        print("\n🚀 ClawHub Publishing:")
        
        cmd = [
            'clawhub', 'publish', str(self.skill_path),
            '--version', version,
            '--changelog', changelog,
            '--tags', tags
        ]
        
        success, output = self._run_command(cmd, capture=True)
        if not success:
            # Check if version already exists
            if "Version already exists" in output:
                print(f"⚠️  Version {version} already exists on ClawHub")
                print("💡 Increment version or use --bump to auto-increment")
                return False
            else:
                print(f"❌ ClawHub publish failed: {output}")
                return False
        
        print(f"✓ Published to ClawHub: {version}")
        return True
    
    def mark_notion_task_done(self, task_name_contains):
        """Mark Notion task as Done"""
        import requests
        
        # Search for task
        url = f"https://api.notion.com/v1/databases/{TASKS_DB_ID}/query"
        headers = {
            "Authorization": f"Bearer {self.notion_api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        payload = {
            "filter": {
                "property": "Name",
                "title": {"contains": task_name_contains}
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return False
        
        results = response.json().get("results", [])
        if not results:
            return False
        
        # Update status to Done
        task_id = results[0]["id"]
        update_url = f"https://api.notion.com/v1/pages/{task_id}"
        update_payload = {
            "properties": {
                "Status": {"status": {"name": "Done"}}
            }
        }
        
        response = requests.patch(update_url, headers=headers, json=update_payload)
        return response.status_code == 200
    
    def publish(self, version, changelog, tags="latest", skip_git=False, skip_clawhub=False):
        """Run complete publishing workflow"""
        print(f"🎯 Publishing Skill: {self.skill_path.name}")
        print(f"📌 Version: {version}")
        print(f"📝 Changelog: {changelog}")
        print(f"🏷️  Tags: {tags}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No actual changes will be made\n")
        
        # Update version in README
        self.update_version_in_readme(version)
        
        # Git operations
        if not skip_git:
            if not self.git_commit_and_push(version, changelog):
                print("\n❌ Git operations failed")
                return False
        else:
            print("\n⏭️  Skipping git operations")
        
        # ClawHub publishing
        if not skip_clawhub:
            if not self.publish_to_clawhub(version, changelog, tags):
                print("\n❌ ClawHub publishing failed")
                return False
        else:
            print("\n⏭️  Skipping ClawHub publishing")
        
        # Mark Notion task done
        skill_name = self.skill_path.name
        if self.mark_notion_task_done(skill_name):
            print(f"\n✓ Marked Notion task as Done")
        
        print("\n✅ Publishing complete!")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Publish agent skill to ClawHub"
    )
    parser.add_argument(
        'skill_path',
        help='Path to skill folder'
    )
    parser.add_argument(
        '--version',
        required=True,
        help='Version (semver format, e.g., 2.3.0)'
    )
    parser.add_argument(
        '--changelog',
        required=True,
        help='Changelog description'
    )
    parser.add_argument(
        '--tags',
        default='latest',
        help='Comma-separated tags (default: latest)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without making changes'
    )
    parser.add_argument(
        '--skip-git',
        action='store_true',
        help='Skip git commit/push'
    )
    parser.add_argument(
        '--skip-clawhub',
        action='store_true',
        help='Skip ClawHub publishing'
    )
    
    args = parser.parse_args()
    
    # Validate version format (basic semver check)
    import re
    if not re.match(r'^\d+\.\d+\.\d+$', args.version):
        print("❌ Invalid version format. Use semver (e.g., 2.3.0)")
        sys.exit(1)
    
    # Create publisher and run
    publisher = SkillPublisher(args.skill_path, dry_run=args.dry_run)
    
    success = publisher.publish(
        version=args.version,
        changelog=args.changelog,
        tags=args.tags,
        skip_git=args.skip_git,
        skip_clawhub=args.skip_clawhub
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
