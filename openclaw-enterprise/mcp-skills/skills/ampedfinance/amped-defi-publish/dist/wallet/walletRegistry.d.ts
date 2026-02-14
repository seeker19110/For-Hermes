/**
 * Wallet Registry
 *
 * Manages wallet resolution by walletId.
 * Supports execution mode (with private key) and prepare mode (address-only).
 *
 * Now integrates with evm-wallet-skill for seamless wallet configuration.
 * @see https://github.com/surfer77/evm-wallet-skill
 */
import { WalletConfig } from '../types';
/**
 * Wallet registry entry
 */
interface WalletEntry extends WalletConfig {
    mode: 'execute' | 'prepare';
}
/**
 * Wallet Registry class for resolving wallet configurations
 */
export declare class WalletRegistry {
    private wallets;
    private skillAdapter;
    constructor();
    /**
     * Load wallet configurations from environment
     *
     * @returns Map of walletId to wallet entry
     */
    private loadWallets;
    /**
     * Get a wallet by its ID (synchronous version)
     * Only checks local registry, not skill adapter
     *
     * @param walletId - The wallet identifier
     * @returns The wallet configuration or null if not found
     */
    getWallet(walletId: string): WalletEntry | null;
    /**
     * Resolve a wallet by its ID (async version)
     * Checks local registry first, then tries skill adapter
     *
     * @param walletId - The wallet identifier
     * @returns The wallet configuration or null if not found
     */
    resolveWallet(walletId: string): Promise<WalletEntry | null>;
    /**
     * Validate a wallet entry
     */
    private validateWallet;
    /**
     * Get the wallet mode (execute or prepare)
     *
     * @returns The current wallet mode
     */
    getMode(): 'execute' | 'prepare';
    /**
     * Check if running in execute mode
     *
     * @returns True if in execute mode
     */
    isExecuteMode(): boolean;
    /**
     * Check if running in prepare mode
     *
     * @returns True if in prepare mode
     */
    isPrepareMode(): boolean;
    /**
     * Get all registered wallet IDs (local + skill)
     *
     * @returns Array of wallet IDs
     */
    getWalletIds(): string[];
    /**
     * Get the count of registered wallets (local + skill)
     *
     * @returns Number of wallets
     */
    getWalletCount(): number;
    /**
     * Reload wallets from environment (useful for hot-reloading)
     */
    reload(): void;
}
/**
 * Get the singleton wallet registry instance
 * @returns The WalletRegistry singleton
 */
export declare function getWalletRegistry(): WalletRegistry;
/**
 * Reset the wallet registry (useful for testing)
 */
export declare function resetWalletRegistry(): void;
export {};
//# sourceMappingURL=walletRegistry.d.ts.map