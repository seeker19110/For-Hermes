/**
 * Wallet Registry
 *
 * Manages wallet resolution by walletId.
 * Supports execution mode (with private key) and prepare mode (address-only).
 *
 * Now integrates with evm-wallet-skill for seamless wallet configuration.
 * @see https://github.com/surfer77/evm-wallet-skill
 */
import { getWalletAdapter } from './skillWalletAdapter';
/**
 * Wallet Registry class for resolving wallet configurations
 */
export class WalletRegistry {
    wallets;
    skillAdapter;
    constructor() {
        this.skillAdapter = getWalletAdapter();
        this.wallets = this.loadWallets();
        // Log skill adapter status
        if (this.skillAdapter.isUsingSkillWallets()) {
            console.log('[walletRegistry] evm-wallet-skill integration active');
        }
    }
    /**
     * Load wallet configurations from environment
     *
     * @returns Map of walletId to wallet entry
     */
    loadWallets() {
        const walletsJson = process.env.AMPED_OC_WALLETS_JSON;
        const mode = process.env.AMPED_OC_MODE || 'execute';
        if (!walletsJson) {
            console.warn('[walletRegistry] AMPED_OC_WALLETS_JSON not set');
            return new Map();
        }
        try {
            const walletConfigs = JSON.parse(walletsJson);
            const wallets = new Map();
            for (const [walletId, config] of Object.entries(walletConfigs)) {
                wallets.set(walletId, {
                    ...config,
                    mode,
                });
            }
            console.log(`[walletRegistry] Loaded ${wallets.size} wallet(s) in ${mode} mode`);
            return wallets;
        }
        catch (error) {
            console.error('[walletRegistry] Failed to parse AMPED_OC_WALLETS_JSON', error);
            return new Map();
        }
    }
    /**
     * Get a wallet by its ID (synchronous version)
     * Only checks local registry, not skill adapter
     *
     * @param walletId - The wallet identifier
     * @returns The wallet configuration or null if not found
     */
    getWallet(walletId) {
        const wallet = this.wallets.get(walletId);
        if (wallet) {
            return this.validateWallet(wallet, walletId);
        }
        console.error(`[walletRegistry] Wallet not found: ${walletId}`);
        return null;
    }
    /**
     * Resolve a wallet by its ID (async version)
     * Checks local registry first, then tries skill adapter
     *
     * @param walletId - The wallet identifier
     * @returns The wallet configuration or null if not found
     */
    async resolveWallet(walletId) {
        // Try local registry first (synchronous)
        const wallet = this.getWallet(walletId);
        if (wallet) {
            return wallet;
        }
        // Try skill adapter (includes ~/.evm-wallet.json)
        if (this.skillAdapter.isUsingSkillWallets()) {
            try {
                const config = await this.skillAdapter.getWalletConfig(walletId);
                const mode = this.getMode();
                return {
                    address: config.address,
                    privateKey: config.privateKey,
                    mode,
                };
            }
            catch (error) {
                console.error(`[walletRegistry] Skill wallet resolution failed: ${error}`);
            }
        }
        console.error(`[walletRegistry] Wallet not found: ${walletId}`);
        return null;
    }
    /**
     * Validate a wallet entry
     */
    validateWallet(wallet, walletId) {
        // In execute mode, validate that private key is present
        if (wallet.mode === 'execute' && !wallet.privateKey) {
            console.error(`[walletRegistry] Wallet ${walletId} missing privateKey in execute mode`);
            return null;
        }
        // Validate address format (basic check)
        if (!wallet.address || !wallet.address.startsWith('0x')) {
            console.error(`[walletRegistry] Wallet ${walletId} has invalid address: ${wallet.address}`);
            return null;
        }
        return wallet;
    }
    /**
     * Get the wallet mode (execute or prepare)
     *
     * @returns The current wallet mode
     */
    getMode() {
        return process.env.AMPED_OC_MODE || 'execute';
    }
    /**
     * Check if running in execute mode
     *
     * @returns True if in execute mode
     */
    isExecuteMode() {
        return this.getMode() === 'execute';
    }
    /**
     * Check if running in prepare mode
     *
     * @returns True if in prepare mode
     */
    isPrepareMode() {
        return this.getMode() === 'prepare';
    }
    /**
     * Get all registered wallet IDs (local + skill)
     *
     * @returns Array of wallet IDs
     */
    getWalletIds() {
        const localIds = Array.from(this.wallets.keys());
        const skillIds = this.skillAdapter.getWalletIds();
        // Merge unique IDs
        return [...new Set([...localIds, ...skillIds])];
    }
    /**
     * Get the count of registered wallets (local + skill)
     *
     * @returns Number of wallets
     */
    getWalletCount() {
        return this.getWalletIds().length;
    }
    /**
     * Reload wallets from environment (useful for hot-reloading)
     */
    reload() {
        this.wallets = this.loadWallets();
    }
}
// Singleton instance
let walletRegistryInstance = null;
/**
 * Get the singleton wallet registry instance
 * @returns The WalletRegistry singleton
 */
export function getWalletRegistry() {
    if (!walletRegistryInstance) {
        walletRegistryInstance = new WalletRegistry();
    }
    return walletRegistryInstance;
}
/**
 * Reset the wallet registry (useful for testing)
 */
export function resetWalletRegistry() {
    walletRegistryInstance = null;
}
//# sourceMappingURL=walletRegistry.js.map