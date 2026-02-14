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
import type { WalletBackendType } from './providers';
export interface BackendConfig {
    backend: WalletBackendType;
    bankrApiKey?: string;
    bankrApiUrl?: string;
}
/**
 * Get the resolved backend configuration
 *
 * Priority:
 * 1. Environment variables
 * 2. Config file
 * 3. Defaults
 */
export declare function getBackendConfig(): BackendConfig;
/**
 * Check if Bankr backend is configured and available
 */
export declare function isBankrConfigured(): boolean;
/**
 * Get Bankr configuration if available
 */
export declare function getBankrConfig(): {
    apiKey: string;
    apiUrl: string;
} | null;
//# sourceMappingURL=backendConfig.d.ts.map