/**
 * Unified Wallet Manager
 *
 * Manages multiple wallet sources with nicknames:
 * - evm-wallet-skill (main)
 * - Bankr (bankr)
 * - Environment variables (custom names)
 *
 * Auto-discovery order:
 * 1. wallets.json config file
 * 2. ~/.evm-wallet.json (evm-wallet-skill) → "main"
 * 3. BANKR_API_KEY env → "bankr"
 * 4. AMPED_OC_WALLETS_JSON env → named wallets
 */
import type { IWalletBackend, WalletInfo, WalletConfig } from './types';
/**
 * Unified wallet manager
 */
export declare class WalletManager {
    private wallets;
    private defaultWallet;
    private initialized;
    /**
     * Initialize the wallet manager
     * Auto-discovers wallets from all sources
     */
    initialize(): Promise<void>;
    /**
     * Load wallets from config file
     */
    private loadConfigFile;
    /**
     * Create backend from config entry
     */
    private createBackendFromConfig;
    /**
     * Auto-discover wallets from environment
     */
    private autoDiscover;
    /**
     * Determine default wallet
     */
    private determineDefault;
    /**
     * Resolve a wallet by nickname
     * @param nickname Optional wallet nickname (uses default if not provided)
     */
    resolve(nickname?: string): Promise<IWalletBackend>;
    /**
     * Check if a wallet exists
     */
    has(nickname: string): Promise<boolean>;
    /**
     * List all available wallets
     */
    listWallets(): Promise<WalletInfo[]>;
    /**
     * Get the default wallet nickname
     */
    getDefaultWalletName(): Promise<string | null>;
    /**
     * Register a new wallet backend
     */
    registerWallet(nickname: string, backend: IWalletBackend): void;
    /**
     * Get available wallet IDs (nicknames)
     * Synchronous version - requires prior initialization
     */
    getAvailableWalletIds(): string[];
    /**
     * Add a new wallet to the config file
     */
    addWallet(nickname: string, config: WalletConfig): Promise<void>;
    /**
     * Rename a wallet
     */
    renameWallet(currentNickname: string, newNickname: string): Promise<void>;
    /**
     * Remove a wallet from config
     */
    removeWallet(nickname: string): Promise<void>;
    /**
     * Set the default wallet
     */
    setDefaultWallet(nickname: string): Promise<void>;
    /**
     * Load config from file (creates empty if doesn't exist)
     */
    private loadConfigFromFile;
    /**
     * Save config to file
     */
    private saveConfigToFile;
    /**
     * Convert a backend to config (for saving auto-discovered wallets)
     */
    private backendToConfig;
    /**
     * Reset the manager (for testing)
     */
    reset(): void;
}
/**
 * Get the singleton WalletManager instance
 */
export declare function getWalletManager(): WalletManager;
/**
 * Reset the singleton (for testing)
 */
export declare function resetWalletManager(): void;
//# sourceMappingURL=walletManager.d.ts.map