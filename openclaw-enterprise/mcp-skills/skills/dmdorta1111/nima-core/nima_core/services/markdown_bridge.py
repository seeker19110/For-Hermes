#!/usr/bin/env python3
"""
NIMA Markdown Bridge — Bidirectional Memory Sync
=================================================
Bridges NIMA's vector store with text-based markdown memory files.

Two operations:
1. export_to_markdown() — NIMA .pt → human-readable .md file
2. ingest_from_markdown() — .md files → NIMA .pt memories

This enables integration with any system that uses markdown memory
(OpenClaw, Obsidian, plain files, etc.)

Usage:
    from nima_core.services.markdown_bridge import MarkdownBridge
    
    bridge = MarkdownBridge(nima)
    
    # Export NIMA memories to markdown
    bridge.export_to_markdown("./memories_export.md")
    
    # Ingest markdown files into NIMA
    bridge.ingest_from_markdown(["./memory/daily.md", "./MEMORY.md"])
    
    # Full bidirectional sync
    bridge.sync(
        markdown_dir="./memory/",
        export_path="./memory/nima_export.md",
    )

Author: NIMA Project
"""

import os
import re
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# Chunking config
MIN_CHUNK_LENGTH = 30
MAX_CHUNK_LENGTH = 500
SIMILARITY_THRESHOLD = 0.7
DEFAULT_IMPORTANCE = 0.6


class MarkdownBridge:
    """Bidirectional bridge between NIMA and markdown memory files."""
    
    def __init__(self, nima, agent_name: str = "Agent"):
        """
        Args:
            nima: NimaCore instance
            agent_name: Name for 'who' field on ingested memories
        """
        self.nima = nima
        self.agent_name = agent_name
    
    # ──────────────────────────────────────────────
    # EXPORT: NIMA → Markdown
    # ──────────────────────────────────────────────
    
    def export_to_markdown(self, output_path: str) -> int:
        """
        Export all NIMA memories to a markdown file.
        
        Args:
            output_path: Where to write the markdown file
        
        Returns:
            Number of memories exported
        """
        memories = self.nima._load_memories()
        if not memories:
            logger.info("No memories to export")
            return 0
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        lines = [
            f"# NIMA Memories Export",
            f"",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Agent:** {self.nima.name}",
            f"**Total Memories:** {len(memories)}",
            f"",
            f"---",
            f"",
        ]
        
        # Sort by importance (most important first)
        sorted_mems = sorted(memories, key=lambda m: m.get('importance', 0), reverse=True)
        
        for i, mem in enumerate(sorted_mems, 1):
            who = mem.get('who', 'unknown')
            what = mem.get('what', '')
            importance = mem.get('importance', 0.5)
            timestamp = mem.get('timestamp', '')
            affect = mem.get('affect', '')
            context = mem.get('context', '')
            
            # Header: truncated text
            preview = what[:60].replace('\n', ' ')
            if len(what) > 60:
                preview += "..."
            
            lines.append(f"### {i}. [{who}] {preview}")
            lines.append(f"")
            lines.append(what)
            lines.append(f"")
            
            meta = []
            if timestamp:
                meta.append(f"📅 {timestamp}")
            if importance:
                emoji = "🔴" if importance > 0.7 else "🟡" if importance > 0.4 else "🟢"
                meta.append(f"{emoji} importance={importance:.2f}")
            if affect:
                meta.append(f"💚 affect={affect}")
            if context and context != 'auto-capture':
                meta.append(f"📎 {context}")
            
            if meta:
                lines.append(" | ".join(meta))
                lines.append(f"")
            
            lines.append(f"---")
            lines.append(f"")
        
        lines.append(f"*Auto-generated from NIMA memory store.*")
        
        content = "\n".join(lines)
        # Atomic write: write to temp file then rename
        import tempfile
        tmp_fd, tmp_path = tempfile.mkstemp(
            dir=str(output.parent), suffix='.tmp', prefix='.nima_export_'
        )
        try:
            with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
                f.write(content)
            Path(tmp_path).replace(output)
        except Exception:
            Path(tmp_path).unlink(missing_ok=True)
            raise
        
        logger.info(f"Exported {len(memories)} memories to {output}")
        return len(memories)
    
    # ──────────────────────────────────────────────
    # INGEST: Markdown → NIMA
    # ──────────────────────────────────────────────
    
    def ingest_from_markdown(
        self,
        file_paths: List[str],
        exclude_patterns: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> Dict:
        """
        Ingest markdown files into NIMA as memories.
        
        Extracts meaningful chunks, deduplicates against existing
        memories, and stores unique ones.
        
        Args:
            file_paths: List of markdown file paths to ingest
            exclude_patterns: Filename patterns to skip (e.g. ["nima_export"])
            dry_run: Preview without writing
        
        Returns:
            Dict with added, duplicates, total_chunks
        """
        exclude_patterns = exclude_patterns or ["nima_export", "nima_memories_export"]
        
        all_chunks = []
        for filepath in file_paths:
            path = Path(filepath)
            
            if not path.exists():
                logger.warning(f"File not found: {path}")
                continue
            
            # Skip excluded patterns
            if any(pat in path.name for pat in exclude_patterns):
                logger.debug(f"Skipping excluded file: {path.name}")
                continue
            
            chunks = self._extract_chunks(path)
            logger.info(f"  {path.name}: {len(chunks)} chunks")
            all_chunks.extend(chunks)
        
        if not all_chunks:
            return {"added": 0, "duplicates": 0, "total_chunks": 0}
        
        # Deduplicate against existing NIMA memories
        existing = self.nima._load_memories()
        unique, dupes = self._deduplicate(all_chunks, existing)
        
        logger.info(f"Dedup: {len(all_chunks)} → {len(unique)} unique, {dupes} duplicates")
        
        if dry_run:
            return {
                "added": 0,
                "would_add": len(unique),
                "duplicates": dupes,
                "total_chunks": len(all_chunks),
                "preview": [c["what"][:80] for c in unique[:10]],
            }
        
        # Store unique chunks
        added = 0
        for chunk in unique:
            success = self.nima.capture(
                who=chunk["who"],
                what=chunk["what"],
                importance=chunk["importance"],
                memory_type=chunk.get("context", "markdown"),
            )
            if success:
                added += 1
        
        logger.info(f"Ingested {added} new memories from markdown")
        
        return {
            "added": added,
            "duplicates": dupes,
            "total_chunks": len(all_chunks),
        }
    
    def ingest_from_directory(
        self,
        directory: str,
        glob_pattern: str = "*.md",
        exclude_patterns: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> Dict:
        """
        Ingest all markdown files from a directory.
        
        Args:
            directory: Directory to scan
            glob_pattern: File pattern (default: *.md)
            exclude_patterns: Filename patterns to skip
            dry_run: Preview without writing
        
        Returns:
            Dict with ingestion results
        """
        dirpath = Path(directory)
        if not dirpath.exists():
            logger.warning(f"Directory not found: {dirpath}")
            return {"added": 0, "error": "directory_not_found"}
        
        files = sorted(dirpath.glob(glob_pattern))
        logger.info(f"Found {len(files)} markdown files in {dirpath}")
        
        return self.ingest_from_markdown(
            [str(f) for f in files],
            exclude_patterns=exclude_patterns,
            dry_run=dry_run,
        )
    
    # ──────────────────────────────────────────────
    # SYNC: Full bidirectional
    # ──────────────────────────────────────────────
    
    def sync(
        self,
        markdown_dir: str,
        export_path: str,
        extra_files: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict:
        """
        Full bidirectional sync.
        
        1. Ingest markdown → NIMA (new content becomes memories)
        2. Export NIMA → markdown (all memories become searchable text)
        
        Args:
            markdown_dir: Directory with markdown memory files
            export_path: Where to write the NIMA export
            extra_files: Additional files to ingest (e.g. MEMORY.md)
            exclude_patterns: Filename patterns to skip during ingest
        
        Returns:
            Dict with ingest and export results
        """
        # Default exclude: the export file itself (prevent circular)
        export_name = Path(export_path).name
        exclude = list(exclude_patterns or [])
        if export_name not in exclude:
            exclude.append(export_name.replace('.md', ''))
        
        # Step 1: Ingest markdown → NIMA
        ingest_result = self.ingest_from_directory(
            markdown_dir,
            exclude_patterns=exclude,
        )
        
        # Also ingest extra files
        if extra_files:
            extra_result = self.ingest_from_markdown(
                extra_files,
                exclude_patterns=exclude,
            )
            ingest_result["added"] += extra_result["added"]
            ingest_result["duplicates"] += extra_result["duplicates"]
        
        # Step 2: Export NIMA → markdown
        exported = self.export_to_markdown(export_path)
        
        return {
            "ingest": ingest_result,
            "export": {"memories_exported": exported, "path": export_path},
        }
    
    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────
    
    def _extract_chunks(self, filepath: Path) -> List[Dict]:
        """Extract meaningful chunks from a markdown file."""
        try:
            text = filepath.read_text(encoding='utf-8')
        except (IOError, UnicodeDecodeError) as e:
            logger.warning(f"Cannot read {filepath}: {e}")
            return []
        
        filename = filepath.name
        chunks = []
        
        # Try to extract date from filename
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', filename)
        file_date = date_match.group(1) if date_match else datetime.now().isoformat()
        
        # Classify source type
        source_type = "notes"
        if "memory" in filename.lower():
            source_type = "long_term_memory"
        elif "research" in filename.lower():
            source_type = "research"
        
        # Split into sections by headers
        sections = re.split(r'\n(?=#{1,3} )', text)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            # Extract header
            header = ""
            body = section
            header_match = re.match(r'^(#{1,3})\s+(.+?)$', section, re.MULTILINE)
            if header_match:
                header = header_match.group(2).strip()
                body = section[header_match.end():].strip()
            
            if not body or len(body) < MIN_CHUNK_LENGTH:
                continue
            
            # Skip code-only sections
            if body.count('```') >= 2 and len(re.sub(r'```[\s\S]*?```', '', body).strip()) < 30:
                continue
            
            # Skip file listings
            lines = [l.strip() for l in body.split('\n') if l.strip()]
            if lines and all(l.startswith('- ') and '/' in l for l in lines):
                continue
            
            # Clean markdown formatting
            clean = re.sub(r'```[\s\S]*?```', '[code]', body)
            clean = re.sub(r'`[^`]+`', '', clean)
            clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
            clean = re.sub(r'\*([^*]+)\*', r'\1', clean)
            clean = re.sub(r'!\[.*?\]\(.*?\)', '', clean)
            clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
            clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
            
            if len(clean) < MIN_CHUNK_LENGTH:
                continue
            
            # Truncate
            what = clean[:MAX_CHUNK_LENGTH]
            if len(clean) > MAX_CHUNK_LENGTH:
                what = what.rsplit(' ', 1)[0] + '...'
            
            # Determine importance
            importance = DEFAULT_IMPORTANCE
            lower = what.lower()
            if any(kw in lower for kw in ['important', 'critical', 'decision', 'lesson', 'remember']):
                importance = 0.8
            if source_type == "long_term_memory":
                importance = max(importance, 0.75)
            
            chunks.append({
                "who": self.agent_name,
                "what": what,
                "importance": importance,
                "timestamp": file_date,
                "context": f"markdown:{source_type}:{filename}",
            })
        
        return chunks
    
    def _deduplicate(
        self,
        new_chunks: List[Dict],
        existing_memories: List[Dict],
    ) -> Tuple[List[Dict], int]:
        """Deduplicate new chunks against existing memories."""
        # Build fingerprint set
        existing_fps: Set[str] = set()
        existing_texts: List[str] = []
        
        for mem in existing_memories:
            what = mem.get("what", "")
            if what:
                existing_fps.add(self._fingerprint(what))
                existing_texts.append(what)
        
        unique = []
        dupes = 0
        
        for chunk in new_chunks:
            what = chunk["what"]
            fp = self._fingerprint(what)
            
            # Stage 1: Exact fingerprint match
            if fp in existing_fps:
                dupes += 1
                continue
            
            # Stage 2: Jaccard similarity (check last 200 for speed)
            is_dupe = False
            for existing_text in existing_texts[-200:]:
                if self._jaccard(what, existing_text) > SIMILARITY_THRESHOLD:
                    is_dupe = True
                    break
            
            if is_dupe:
                dupes += 1
                continue
            
            # Stage 3: Dedup within batch
            internal_dupe = False
            for prev in unique:
                if self._jaccard(what, prev["what"]) > SIMILARITY_THRESHOLD:
                    internal_dupe = True
                    break
            
            if internal_dupe:
                dupes += 1
                continue
            
            existing_fps.add(fp)
            existing_texts.append(what)
            unique.append(chunk)
        
        return unique, dupes
    
    @staticmethod
    def _fingerprint(text: str) -> str:
        """Compute normalized fingerprint for dedup."""
        normalized = re.sub(r'[^\w\s]', '', text.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return hashlib.md5(normalized[:200].encode()).hexdigest()
    
    @staticmethod
    def _jaccard(text1: str, text2: str) -> float:
        """Word-level Jaccard similarity."""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union)
