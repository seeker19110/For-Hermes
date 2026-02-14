const fs = require('fs');
const { execSync } = require('child_process');
const path = require('path');

// Helper to parse arguments
function parseArgs() {
  const args = process.argv.slice(2);
  const parsed = {
    command: args[0],
    pattern: null,
    pid: null,
    force: false,
    json: false
  };

  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--pattern') parsed.pattern = args[++i];
    if (args[i] === '--pid') parsed.pid = args[++i];
    if (args[i] === '--force') parsed.force = true;
    if (args[i] === '--json') parsed.json = true;
  }
  return parsed;
}

// Command: List processes
function listProcesses(pattern, jsonOutput) {
  try {
    // Use ps aux to get full list
    // Output format: USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND
    const output = execSync('ps aux', { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
    const lines = output.trim().split('\n');
    const headers = lines[0].split(/\s+/);
    
    let processes = [];
    
    // Parse lines (skipping header)
    for (let i = 1; i < lines.length; i++) {
      const parts = lines[i].trim().split(/\s+/);
      if (parts.length < 11) continue;
      
      const pid = parts[1];
      const user = parts[0];
      const cpu = parts[2];
      const mem = parts[3];
      // Command is the rest of the line
      const command = parts.slice(10).join(' ');
      
      if (!pattern || command.includes(pattern)) {
        processes.push({ pid, user, cpu, mem, command });
      }
    }

    if (jsonOutput) {
      console.log(JSON.stringify(processes, null, 2));
    } else {
      if (processes.length === 0) {
        console.log(`No processes found matching pattern: ${pattern || '*'}`);
      } else {
        console.log(`Found ${processes.length} processes:`);
        processes.forEach(p => {
          console.log(`[${p.pid}] ${p.user} (CPU:${p.cpu}% MEM:${p.mem}%) ${p.command.substring(0, 100)}`);
        });
      }
    }
  } catch (error) {
    console.error(`Error listing processes: ${error.message}`);
    process.exit(1);
  }
}

// Command: Kill process
function killProcess(pid, pattern, force) {
  if (!pid && !pattern) {
    console.error("Error: Must provide --pid or --pattern for kill command.");
    process.exit(1);
  }

  // Safety list of critical processes to NEVER kill via pattern
  const PROTECTED_PATTERNS = [
    'openclaw', 'gateway', 'sshd', 'systemd', 'init', 'bash', 'sh'
  ];

  if (pattern) {
    // Safety check for patterns
    if (PROTECTED_PATTERNS.some(p => pattern.includes(p))) {
      console.error(`Error: Pattern '${pattern}' matches protected system processes. Operation aborted.`);
      process.exit(1);
    }
    
    if (!force) {
      console.error("Error: Killing by pattern requires --force flag to prevent accidents.");
      process.exit(1);
    }

    try {
      // Find PIDs first
      const pgrep = execSync(`pgrep -f "${pattern}"`, { encoding: 'utf8' }).trim();
      if (!pgrep) {
        console.log(`No processes found matching '${pattern}'`);
        return;
      }
      
      const pids = pgrep.split('\n');
      console.log(`Killing ${pids.length} processes matching '${pattern}'...`);
      
      pids.forEach(p => {
        try {
          process.kill(p, 'SIGTERM');
          console.log(`Sent SIGTERM to ${p}`);
        } catch (e) {
          console.error(`Failed to kill ${p}: ${e.message}`);
        }
      });
      
    } catch (e) {
      console.log(`No processes found matching '${pattern}'`);
    }

  } else if (pid) {
    try {
      process.kill(pid, 'SIGTERM');
      console.log(`Sent SIGTERM to PID ${pid}`);
    } catch (e) {
      console.error(`Failed to kill PID ${pid}: ${e.message}`);
      process.exit(1);
    }
  }
}

// Main execution
const args = parseArgs();

if (args.command === 'list') {
  listProcesses(args.pattern, args.json);
} else if (args.command === 'kill') {
  killProcess(args.pid, args.pattern, args.force);
} else {
  console.log(`
Usage:
  node skills/process-manager/index.js list [--pattern "text"] [--json]
  node skills/process-manager/index.js kill --pid <id>
  node skills/process-manager/index.js kill --pattern "text" --force
  `);
}
