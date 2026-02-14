const fs = require('fs');
const path = require('path');

const ARGS = process.argv.slice(2);
const DRY_RUN = ARGS.includes('--dry-run');
const EXECUTE = ARGS.includes('--execute');

if (!DRY_RUN && !EXECUTE) {
  console.log('Usage: node skills/workspace-cleaner/index.js --dry-run | --execute');
  process.exit(1);
}

const WORKSPACE_ROOT = process.cwd();
const TEMP_DIR = path.join(WORKSPACE_ROOT, 'temp');
const MAX_AGE_MS = 7 * 24 * 60 * 60 * 1000; // 7 days

if (!fs.existsSync(TEMP_DIR)) {
  console.log(`[Cleaner] Temp directory not found: ${TEMP_DIR}`);
  process.exit(0);
}

function walk(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  files.forEach(file => {
    const filePath = path.join(dir, file);
    try {
      const stat = fs.lstatSync(filePath);
      if (stat.isDirectory()) {
        fileList = walk(filePath, fileList);
      } else {
        fileList.push({ path: filePath, mtime: stat.mtimeMs });
      }
    } catch (e) {
      // Ignore broken links or access errors
    }
  });
  return fileList;
}

const now = Date.now();
const allFiles = walk(TEMP_DIR);
const toDelete = allFiles.filter(f => {
  const age = now - f.mtime;
  return age > MAX_AGE_MS;
});

console.log(`[Cleaner] Found ${toDelete.length} files older than 7 days in temp/`);

toDelete.forEach(f => {
  if (DRY_RUN) {
    console.log(`[DryRun] Would delete: ${path.relative(WORKSPACE_ROOT, f.path)}`);
  } else if (EXECUTE) {
    try {
      fs.unlinkSync(f.path);
      console.log(`[Deleted] ${path.relative(WORKSPACE_ROOT, f.path)}`);
    } catch (e) {
      console.error(`[Error] Failed to delete ${f.path}: ${e.message}`);
    }
  }
});

// Clean empty dirs (simple pass)
if (EXECUTE) {
    // Implementation omitted for safety in v1, focus on files first
}
