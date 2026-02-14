/**
 * NIMA Auto-Recall Hook (Ultra-Fast Version)
 * 
 * Queries NIMA memory on session bootstrap using lightweight keyword search.
 * NO heavy ML models loaded - pure text matching for instant results.
 */

import { execFileSync } from "child_process";
import { existsSync, readFileSync } from "fs";
import { join } from "path";

interface HookEvent {
  type: string;
  action: string;
  sessionKey: string;
  timestamp: Date;
  messages: string[];
  context: {
    workspaceDir?: string;
    sessionFile?: string;
    bootstrapFiles?: Array<{ path: string; content: string; source: string }>;
    cfg?: Record<string, unknown>;
  };
}

type HookHandler = (event: HookEvent) => Promise<void> | void;

/**
 * Extract recent conversation text from session transcript
 */
function extractRecentContext(sessionFile: string, maxLines: number = 100): string {
  try {
    const content = readFileSync(sessionFile, "utf-8");
    const lines = content.split("\n").slice(-maxLines);
    
    const messages: string[] = [];
    let currentRole = "";
    let currentText = "";

    for (const line of lines) {
      if (line.startsWith("## User") || line.startsWith("## Assistant")) {
        if (currentText && currentRole) {
          messages.push(`${currentRole}: ${currentText.trim()}`);
        }
        currentRole = line.startsWith("## User") ? "User" : "Assistant";
        currentText = "";
      } else if (currentRole && line.trim() && !line.startsWith("---")) {
        currentText += line + " ";
      }
    }

    if (currentText && currentRole) {
      messages.push(`${currentRole}: ${currentText.trim()}`);
    }

    return messages.slice(-5).join("\n\n") || "";
  } catch (err) {
    return "";
  }
}

/**
 * Query NIMA using ultra-fast CLI (no heavy models loaded)
 */
function queryNIMAFast(workspaceDir: string, query: string, limit: number): string | null {
  try {
    // Use lightweight recall script - NO embeddings, NO model loading
    const scriptPath = join(workspaceDir, "nima-core", "nima_core", "cli", "recall_fast.py");
    
    // Fallback: try system path if not in workspace
    const args = existsSync(scriptPath) 
      ? [scriptPath, query, "--top-k", String(limit)]
      : ["-m", "nima_core.cli.recall_fast", query, "--top-k", String(limit)];
    
    const result = execFileSync("python3", args, {
      cwd: workspaceDir,
      timeout: 5000, // 5 second timeout (was 15s)
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();

    return result || null;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    // Silently fail - don't spam logs on timeout
    if (!msg.includes("ETIMEDOUT") && !msg.includes("SIGTERM")) {
      console.error("[nima-recall] Query error:", msg.substring(0, 100));
    }
    return null;
  }
}

/**
 * Format results as markdown
 */
function formatResults(raw: string, querySnippet: string): string {
  const lines = raw.split("\n").filter((l) => l.trim());
  if (lines.length === 0) return "";

  let md = `# 🔮 NIMA Recall\n\n`;
  md += `**Context:** ${querySnippet.substring(0, 100)}${querySnippet.length > 100 ? "..." : ""}\n\n`;

  for (let i = 0; i < lines.length; i++) {
    const parts = lines[i].split("|");
    const who = parts[0]?.trim() || "?";
    const what = parts.slice(1).join("|").trim() || lines[i];
    const truncated = what.length > 150 ? what.substring(0, 150) + "..." : what;
    md += `**[${i + 1}]** ${who}: ${truncated}\n\n`;
  }

  md += `---\n*${lines.length} memories retrieved*\n`;
  return md;
}

const handler: HookHandler = async (event) => {
  // Only handle bootstrap
  if (event.type !== "agent" || event.action !== "bootstrap") return;

  // Skip non-conversational sessions
  if (event.sessionKey?.includes(":subagent:")) return;
  if (event.sessionKey?.includes("heartbeat")) return;

  const workspaceDir = event.context.workspaceDir;
  if (!workspaceDir) return;

  // Config
  const hookConfig = (event.context.cfg as any)?.hooks?.internal?.entries?.["nima-recall"] || {};
  if (hookConfig.enabled === false) return;
  const limit = hookConfig.limit ?? 3;

  try {
    // Extract conversation context
    let queryContext = "";
    if (event.context.sessionFile && existsSync(event.context.sessionFile)) {
      queryContext = extractRecentContext(event.context.sessionFile);
    }

    // Need meaningful context to query
    if (queryContext.length < 10) {
      return;
    }

    // Query NIMA (ultra-fast, no model loading)
    const results = queryNIMAFast(workspaceDir, queryContext, limit);
    if (!results) return;

    // Format and inject
    const md = formatResults(results, queryContext);
    if (!md) return;

    if (!event.context.bootstrapFiles) event.context.bootstrapFiles = [];
    event.context.bootstrapFiles.push({
      path: "NIMA_RECALL.md",
      content: md,
      source: "nima-recall",
    });

    console.log(`[nima-recall] ✓ Injected ${limit} memories`);
  } catch (err) {
    // Silent fail - don't block agent startup
  }
};

export default handler;
