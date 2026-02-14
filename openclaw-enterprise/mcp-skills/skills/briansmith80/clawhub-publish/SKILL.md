---
name: clawhub-publish
description: Publish and update agent skills to ClawHub registry. Use when publishing new skill versions, updating existing skills, or managing ClawHub publications. Handles version checking, git commits, GitHub pushing, and ClawHub publishing workflow.
---

# ClawHub Publishing Workflow

Automate the complete workflow for publishing agent skills to ClawHub, including version management, git operations, and registry publishing.

## Prerequisites

- ClawHub CLI installed (`npm install -g clawhub`)
- Authenticated with ClawHub (`clawhub login`)
- GitHub Personal Access Token in Notion Password Manager
- Git repository configured with remote origin

## Usage

**Publish a new version:**
```bash
python3 scripts/publish-skill.py /path/to/skill-folder --version 2.3.0 --changelog "Bug fixes and improvements"
```

**Dry run (no actual publishing):**
```bash
python3 scripts/publish-skill.py /path/to/skill-folder --version 2.3.0 --dry-run
```

**Auto-increment patch version:**
```bash
python3 scripts/publish-skill.py /path/to/skill-folder --bump patch --changelog "Minor fixes"
```

## Workflow Steps

The script performs these steps in order:

1. **Version Check**
   - Validates semver format
   - Checks if version already exists on ClawHub
   - Updates version in README.md and other relevant files

2. **Git Operations**
   - Stages all changes
   - Creates commit with version and changelog
   - Retrieves GitHub token from Notion Password Manager
   - Pushes to GitHub origin/main

3. **ClawHub Publishing**
   - Publishes skill to ClawHub registry
   - Applies tags (latest, security-fix, etc.)
   - Returns publication ID

4. **Notion Task Update**
   - Marks related Notion tasks as "Done"
   - Creates new task for next version if needed

## Examples

**Security update:**
```bash
python3 scripts/publish-skill.py ~/skills/my-skill \
  --version 2.2.1 \
  --changelog "SECURITY FIX: Patched command injection vulnerability" \
  --tags "latest,security-fix"
```

**Major release:**
```bash
python3 scripts/publish-skill.py ~/skills/my-skill \
  --bump major \
  --changelog "Breaking changes: New API, removed deprecated methods"
```

**Feature release:**
```bash
python3 scripts/publish-skill.py ~/skills/my-skill \
  --bump minor \
  --changelog "Added OAuth2 support and batch operations"
```

## Options

- `--version <semver>` - Explicit version (e.g., 2.3.0)
- `--bump <major|minor|patch>` - Auto-increment version
- `--changelog <text>` - Changelog description (required)
- `--tags <tags>` - Comma-separated tags (default: "latest")
- `--dry-run` - Preview without publishing
- `--skip-git` - Skip git commit/push
- `--skip-clawhub` - Skip ClawHub publishing
- `--notion-task <id>` - Mark specific Notion task as done

## Configuration

**GitHub Token Location:**
- Stored in Notion Password Manager
- Database ID: `26c29e15-c2b5-810e-97b8-dcd41413d230`
- Search query: "GitHub Personal Access Token"

**ClawHub Authentication:**
- Requires prior `clawhub login`
- Token stored in `~/.config/clawhub/`

## Common Workflows

### Security Patch Workflow

1. Fix security vulnerability in code
2. Update SECURITY.md with details
3. Run tests to verify fix
4. Publish with security tag:
   ```bash
   python3 scripts/publish-skill.py /path/to/skill \
     --bump patch \
     --changelog "Security fix: [description]" \
     --tags "latest,security-fix"
   ```

### New Feature Workflow

1. Develop and test new feature
2. Update README.md with examples
3. Update CHANGELOG.md
4. Publish minor version:
   ```bash
   python3 scripts/publish-skill.py /path/to/skill \
     --bump minor \
     --changelog "Added [feature name] with [capabilities]"
   ```

### Breaking Changes Workflow

1. Make breaking API changes
2. Update CHANGELOG.md with migration guide
3. Update documentation
4. Publish major version:
   ```bash
   python3 scripts/publish-skill.py /path/to/skill \
     --bump major \
     --changelog "BREAKING: [changes] - see CHANGELOG for migration"
   ```

## Error Handling

**"Version already exists":**
- Increment version number
- Or use `--bump patch` to auto-increment

**"Git authentication failed":**
- Verify GitHub token in Notion
- Check token has `repo` permissions
- Ensure token hasn't expired

**"ClawHub publish timeout":**
- Retry with same version
- ClawHub may have cached the attempt

**"Notion API error":**
- Check Notion API key in `~/.config/notion/api_key`
- Verify database IDs are correct

## Security Notes

- GitHub token stored securely in Notion (encrypted)
- Token only retrieved when needed for git push
- Token never logged or displayed
- Notion API key stored with 0600 permissions

## Automation

**Schedule monthly skill updates:**
```bash
# Add to cron or OpenClaw scheduler
0 9 1 * * cd /root/clawd/skills/my-skill && python3 /root/clawd/skills/clawhub-publish/scripts/publish-skill.py . --bump patch --changelog "Monthly maintenance update"
```

**Auto-publish on git push:**
```bash
# Add to .git/hooks/post-commit
python3 /root/clawd/skills/clawhub-publish/scripts/publish-skill.py . --auto-version
```
