---
name: Video
description: Process, edit, and optimize videos for any platform with compression, format conversion, captioning, and repurposing workflows.
---

## Core Capabilities

| Task | Method |
|------|--------|
| Convert/compress | FFmpeg (see `commands.md`) |
| Generate captions | Whisper transcription → SRT/VTT |
| Change aspect ratio | Crop, pad, or smart reframe |
| Clean audio | Normalize, denoise, enhance |
| Batch operations | Process entire folders in one run |

---

## Quick Reference

| Situation | Load |
|-----------|------|
| Platform specs (YouTube, TikTok, Instagram) | `platforms.md` |
| FFmpeg commands by task | `commands.md` |
| Quality/compression settings | `quality.md` |
| Workflow by use case | `workflows.md` |

---

## Workspace

Store video projects in `~/video/`:
```
~/video/
├── input/       # Source files
├── output/      # Processed results
├── srt/         # Generated subtitles
└── thumbnails/  # Extracted frames
```

---

## Execution Pattern

1. **Clarify target** — What platform? What format? What file size limit?
2. **Check source** — `ffprobe` to get codec, resolution, duration, audio
3. **Process** — FFmpeg for transformation (commands in `commands.md`)
4. **Verify** — Confirm output meets specs before delivering
5. **Clean up** — Offer to delete intermediates

---

## Common Requests → Actions

| User says | Agent does |
|-----------|------------|
| "Make this work for TikTok" | Reframe to 9:16, check duration ≤3min, compress |
| "Add subtitles" | Whisper → SRT → burn-in or deliver separately |
| "Compress for WhatsApp" | Target <64MB, H.264, AAC, maintain quality |
| "Extract audio" | `-vn -acodec mp3` or `-acodec copy` |
| "Make a GIF" | Extract frames, optimize palette, loop |
| "Split into clips" | Cut at timestamps with `-ss` and `-t` |

---

## Quality Rules

- **Always re-encode audio to AAC** for maximum compatibility
- **Use `-movflags +faststart`** for web playback
- **CRF 23** is good default for H.264 (lower = better quality, bigger file)
- **Check before delivering** — verify duration, file size, playability
