import * as fs from "fs";
import * as path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
export const CONFIG_JSON_PATH = path.resolve(__dirname, "..", "config.json");

export interface ConfigJson {
  SESSION_TOKEN?: {
    token: string;
    expiry: string;
  };
  LITE_AGENT_API_KEY?: string;
  SELLER_PID?: number;
}

export function readConfig(): ConfigJson {
  if (!fs.existsSync(CONFIG_JSON_PATH)) {
    return {};
  }
  try {
    const content = fs.readFileSync(CONFIG_JSON_PATH, "utf-8");
    return JSON.parse(content);
  } catch (err) {
    return {};
  }
}

export function writeConfig(config: ConfigJson): void {
  try {
    fs.writeFileSync(CONFIG_JSON_PATH, JSON.stringify(config, null, 2) + "\n");
  } catch (err) {
    console.error(`Failed to write config.json: ${err}`);
  }
}

export function isProcessRunning(pid: number): boolean {
  try {
    process.kill(pid, 0);
    return true;
  } catch (err: any) {
    return err.code !== "ESRCH";
  }
}

export function writePidToConfig(pid: number): void {
  try {
    const config = readConfig();
    config.SELLER_PID = pid;
    writeConfig(config);
  } catch (err) {
    console.error(`Failed to write PID to config.json: ${err}`);
  }
}

export function removePidFromConfig(): void {
  try {
    const config = readConfig();
    if (config.SELLER_PID !== undefined) {
      delete config.SELLER_PID;
      writeConfig(config);
    }
  } catch (err) {
    // Silently fail - config cleanup is best effort
  }
}

export function checkForExistingProcess(): void {
  const config = readConfig();

  if (config.SELLER_PID !== undefined) {
    if (isProcessRunning(config.SELLER_PID)) {
      console.error(
        `Seller process already running with PID: ${config.SELLER_PID})`
      );
      console.error(
        "Please stop the existing process before starting a new one"
      );
      process.exit(1);
    } else {
      removePidFromConfig();
    }
  }
}
