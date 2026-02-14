#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// --- Config ---
const MEMORY_DIR = process.env.MEMORY_DIR || path.resolve(__dirname, '../../memory');
const PERSONA_DIR = path.join(MEMORY_DIR, 'personas');
const TEMPLATE_FILE = path.join(__dirname, 'template.md');

// --- CLI ---
const args = process.argv.slice(2);
const command = args[0];
const subArgs = args.slice(1);

function help() {
  console.log(`
Usage:
  node skills/persona-manager/index.js <command> [options]

Commands:
  list                 List all available personas
  read <name>          Read a persona file (e.g. "sage_planning")
  create <name>        Create a new persona from template
  delete <name>        Delete a persona
  help                 Show this help

Examples:
  node skills/persona-manager/index.js list
  node skills/persona-manager/index.js create my_persona
  node skills/persona-manager/index.js read my_persona
`);
}

function ensureDir() {
  if (!fs.existsSync(PERSONA_DIR)) {
    fs.mkdirSync(PERSONA_DIR, { recursive: true });
  }
}

function listPersonas() {
  ensureDir();
  const files = fs.readdirSync(PERSONA_DIR);
  const personas = files
    .filter(f => f.endsWith('.md') || f.endsWith('.json'))
    .map(f => {
      const ext = path.extname(f);
      const name = path.basename(f, ext);
      return { name, file: f };
    });

  if (personas.length === 0) {
    console.log("No personas found.");
    return;
  }

  console.log("Available Personas:");
  personas.forEach(p => {
    console.log(`- ${p.name} (${p.file})`);
  });
}

function readPersona(name) {
  ensureDir();
  const mdFile = path.join(PERSONA_DIR, `${name}.md`);
  const jsonFile = path.join(PERSONA_DIR, `${name}.json`);

  if (fs.existsSync(mdFile)) {
    console.log(fs.readFileSync(mdFile, 'utf8'));
  } else if (fs.existsSync(jsonFile)) {
    console.log(fs.readFileSync(jsonFile, 'utf8'));
  } else {
    console.error(`Persona "${name}" not found.`);
    process.exit(1);
  }
}

function createPersona(name) {
  ensureDir();
  if (!name) {
    console.error("Error: Missing persona name.");
    process.exit(1);
  }

  const targetFile = path.join(PERSONA_DIR, `${name}.md`);
  if (fs.existsSync(targetFile)) {
    console.error(`Error: Persona "${name}" already exists.`);
    process.exit(1);
  }

  let template = "";
  if (fs.existsSync(TEMPLATE_FILE)) {
    template = fs.readFileSync(TEMPLATE_FILE, 'utf8');
  } else {
    template = `# Persona: ${name}\n\n**Trigger**: [Describe when to activate]\n\n## 1. Interaction Protocol\n[Define style here]\n\n## 2. Thinking Chain\n[Define internal logic]\n`;
  }

  // Replace placeholders if any
  template = template.replace(/{{NAME}}/g, name);

  fs.writeFileSync(targetFile, template);
  console.log(`Created persona: ${targetFile}`);
}

function deletePersona(name) {
  ensureDir();
  const mdFile = path.join(PERSONA_DIR, `${name}.md`);
  const jsonFile = path.join(PERSONA_DIR, `${name}.json`);

  if (fs.existsSync(mdFile)) {
    fs.unlinkSync(mdFile);
    console.log(`Deleted: ${mdFile}`);
  } else if (fs.existsSync(jsonFile)) {
    fs.unlinkSync(jsonFile);
    console.log(`Deleted: ${jsonFile}`);
  } else {
    console.error(`Persona "${name}" not found.`);
    process.exit(1);
  }
}

// --- Main ---
switch (command) {
  case 'list':
    listPersonas();
    break;
  case 'read':
    readPersona(subArgs[0]);
    break;
  case 'create':
    createPersona(subArgs[0]);
    break;
  case 'delete':
    deletePersona(subArgs[0]);
    break;
  default:
    help();
    break;
}
