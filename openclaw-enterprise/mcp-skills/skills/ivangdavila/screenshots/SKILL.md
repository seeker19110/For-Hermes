---
name: Screenshots
description: Create professional App Store and Google Play screenshots with automatic sizing, device frames, marketing copy, and iterative visual learning.
---

## Situation Detection

| Context | Load |
|---------|------|
| Need exact dimensions for stores | `specs.md` |
| Creating marketing text overlays | `text-style.md` |
| Choosing visual templates by category | `templates.md` |
| Full creation workflow | `workflow.md` |

---

## Workspace

Store all screenshot projects in `~/screenshots/`:
```
~/screenshots/
├── {app-slug}/
│   ├── config.md          # Brand: colors, fonts, style
│   ├── raw/               # Raw simulator/device captures
│   ├── v1/                # Version 1 exports
│   ├── v2/                # Version 2 (after changes)
│   └── latest -> v2/      # Symlink to current
├── templates/             # Reusable visual templates
└── learnings.md           # Visual patterns that work
```

---

## Core Workflow

1. **Intake** — Get raw screenshots + app icon + brand colors
2. **Size** — Generate all required dimensions per `specs.md`
3. **Style** — Apply backgrounds, device frames, text overlays
4. **Review** — Use vision to verify quality before sending
5. **Iterate** — Adjust based on user feedback
6. **Export** — Organize by store/device/language

---

## Quality Checklist (Before Sending)

Use vision model to verify EVERY screenshot set:
- [ ] Text readable at thumbnail size?
- [ ] No text in unsafe zones (corners, notch area)?
- [ ] Consistent style across all screenshots?
- [ ] Device frames match the target size?
- [ ] Colors harmonious with app branding?

**If ANY check fails** → fix before presenting to user.

---

## User Preferences (Auto-Learn)

### Style
<!-- dominant-color | gradient | minimal | dark | light -->

### Fonts
<!-- preferred headline fonts -->

### Device Frames
<!-- with-frame | frameless | floating -->

### Copy Tone
<!-- punchy | descriptive | minimal -->

---

## Versioning Rules

- **Never overwrite** — each batch goes in `v{n}/`
- **Symlink `latest`** to current approved version
- **config.md** stores brand decisions for regeneration
- **Compare versions** when user says "go back to the old style"

---

## Learning Loop

After each project, update the learnings file (`~/screenshots/learnings.md`):
- Templates that converted well
- Font/size combinations that worked
- Background styles by app category
- Text patterns that got positive feedback

Check the learnings file before starting new projects. See `feedback.md` for detailed learning system.
