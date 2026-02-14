/**
 * EVM Wallet Skill Adapter
 *
 * Integrates with the evm-wallet-skill to reuse existing wallet configuration
 * instead of requiring custom AMPED_OC_WALLETS_JSON.
 *
 * Supports multiple wallet sources:
 * - ~/.evm-wallet.json (evm-wallet-skill default location)
 * - EVM_WALLETS_JSON environment variable
 * - WALLET_CONFIG_JSON environment variable
 *
 * @see https://github.com/surfer77/evm-wallet-skill
 */
/**
 * Wallet information from evm-wallet-skill
 */
export interface EvmWalletInfo {
    id: string;
    address: string;
    chainId?: number;
    provider?: 'privateKey' | 'kms' | 'hardware' | 'web3Auth';
}
/**
 * Wallet adapter options
 */
export interface WalletAdapterOptions {
    preferSkill?: boolean;
    walletId?: string;
}
/**
 * EVM Wallet Skill Adapter
 */
export declare class EvmWalletSkillAdapter {
    private skillWallets;
    private skillRpcs;
    private useSkill;
    constructor(options?: WalletAdapterOptions);
    /**
     * Load configuration from evm-wallet-skill
     * Checks multiple sources in order:
     * 1. ~/.evm-wallet.json (evm-wallet-skill default)
     * 2. EVM_WALLETS_JSON environment variable
     * 3. WALLET_CONFIG_JSON environment variable
     */
    private loadSkillConfig;
    /**
     * Load wallet from ~/.evm-wallet.json (evm-wallet-skill format)
     */
    private loadEvmWalletFile;
    /**
     * Load wallets from environment variables
     */
    private loadEnvWallets;
    /**
     * Load RPC URLs - uses defaults, then overrides with environment variables
     */
    private loadEnvRpcs;
    /**
     * Get wallet address - tries skill first, then legacy config
     */
    getWalletAddress(walletId?: string): Promise<string>;
    /**
     * Get wallet private key - for signing transactions
     */
    getPrivateKey(walletId?: string): Promise<string | null>;
    /**
     * Get full wallet config (address + privateKey if available)
     */
    getWalletConfig(walletId?: string): Promise<{
        address: string;
        privateKey?: string;
    }>;
    /**
     * Get RPC URL - tries skill first, then legacy config
     */
    getRpcUrl(chainId: string | number): Promise<string>;
    /**
     * Check if using skill wallets
     */
    isUsingSkillWallets(): boolean;
    /**
     * Check if using skill RPCs
     */
    isUsingSkillRpcs(): boolean;
    /**
     * Get all skill wallet IDs
     */
    getWalletIds(): string[];
    /**
     * Get all skill RPC chain IDs
     */
    getRpcChainIds(): string[];
}
export declare function getWalletAdapter(options?: WalletAdapterOptions): EvmWalletSkillAdapter;
export declare function resetWalletAdapter(): void;
//# sourceMappingURL=skillWalletAdapter.d.ts.map