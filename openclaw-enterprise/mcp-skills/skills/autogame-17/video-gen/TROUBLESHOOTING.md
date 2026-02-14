# Troubleshooting

## Issue: MODULE_NOT_FOUND (dotenv, commander)

**Symptom:**
Running `node index.js` fails with:
```
Error: Cannot find module 'dotenv'
```
or
```
Error: Cannot find module 'commander'
```

**Cause:**
Dependencies were not installed after restoring the skill from backup or git. The `node_modules` folder was missing or empty.

**Solution:**
Run `npm install` inside the skill directory to restore dependencies from `package.json`.

```bash
cd skills/video-gen
npm install
```

**Date:** 2026-02-07
