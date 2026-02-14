/**
 * Wallet Backend Configuration
 *
 * Detects and configures the appropriate wallet backend based on
 * environment variables or config file.
 *
 * Supported backends:
 * - localKey (default): Uses evm-wallet-skill local private keys
 * - bankr: Uses Bankr Agent API for transaction execution
 */
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
/**
 * Default configuration
 */
const DEFAULT_CONFIG = {
    backend: 'localKey',
};
/**
 * Path to plugin config file
 */
function getConfigPath() {
    return join(homedir(), '.openclaw', 'extensions', 'amped-defi', 'config.json');
}
/**
 * Load configuration from file
 */
function loadConfigFile() {
    const configPath = getConfigPath();
    if (!existsSync(configPath)) {
        return null;
    }
    try {
        const content = readFileSync(configPath, 'utf-8');
        const config = JSON.parse(content);
        return {
            backend: config.walletBackend,
            bankrApiKey: config.bankrApiKey,
            bankrApiUrl: config.bankrApiUrl,
        };
    }
    catch (error) {
        console.warn('[backendConfig] Failed to load config file:', error);
        return null;
    }
}
/**
 * Load configuration from environment variables
 */
function loadEnvConfig() {
    const config = {};
    // Check for explicit backend selection
    const backendEnv = process.env.AMPED_OC_WALLET_BACKEND;
    if (backendEnv === 'bankr' || backendEnv === 'localKey') {
        config.backend = backendEnv;
    }
    // Check for Bankr API key (implies bankr backend)
    const bankrApiKey = process.env.BANKR_API_KEY;
    if (bankrApiKey) {
        config.bankrApiKey = bankrApiKey;
        // Auto-select bankr backend if API key is present
        if (!config.backend) {
            config.backend = 'bankr';
        }
    }
    // Optional Bankr API URL override
    const bankrApiUrl = process.env.BANKR_API_URL;
    if (bankrApiUrl) {
        config.bankrApiUrl = bankrApiUrl;
    }
    return config;
}
/**
 * Get the resolved backend configuration
 *
 * Priority:
 * 1. Environment variables
 * 2. Config file
 * 3. Defaults
 */
export function getBackendConfig() {
    const fileConfig = loadConfigFile() || {};
    const envConfig = loadEnvConfig();
    // Merge with priority: env > file > default
    const config = {
        ...DEFAULT_CONFIG,
        ...fileConfig,
        ...envConfig,
    };
    // Validate bankr configuration
    if (config.backend === 'bankr' && !config.bankrApiKey) {
        console.warn('[backendConfig] Bankr backend selected but no API key provided');
        console.warn('[backendConfig] Set BANKR_API_KEY environment variable or add bankrApiKey to config.json');
        console.warn('[backendConfig] Falling back to localKey backend');
        config.backend = 'localKey';
    }
    // Set default Bankr API URL if not specified
    if (config.backend === 'bankr' && !config.bankrApiUrl) {
        config.bankrApiUrl = 'https://api.bankr.bot';
    }
    console.log(`[backendConfig] Using wallet backend: ${config.backend}`);
    return config;
}
/**
 * Check if Bankr backend is configured and available
 */
export function isBankrConfigured() {
    const config = getBackendConfig();
    return config.backend === 'bankr' && !!config.bankrApiKey;
}
/**
 * Get Bankr configuration if available
 */
export function getBankrConfig() {
    const config = getBackendConfig();
    if (config.backend !== 'bankr' || !config.bankrApiKey) {
        return null;
    }
    return {
        apiKey: config.bankrApiKey,
        apiUrl: config.bankrApiUrl || 'https://api.bankr.bot',
    };
}
//# sourceMappingURL=backendConfig.js.map