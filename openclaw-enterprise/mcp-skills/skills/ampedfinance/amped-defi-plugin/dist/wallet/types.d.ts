/**
 * Wallet Types - Multi-source wallet management
 *
 * Supports:
 * - evm-wallet-skill (local key from ~/.evm-wallet.json)
 * - Bankr (API-based, limited chains)
 * - Environment variables (AMPED_OC_WALLETS_JSON)
 */
import type { Address, Hash } from 'viem';
/**
 * Supported wallet backend types
 */
export type WalletBackendType = 'evm-wallet-skill' | 'bankr' | 'env';
/**
 * Raw transaction for Bankr submission
 */
export interface RawTransaction {
    to: Address;
    data: `0x${string}`;
    value: string;
    chainId: number;
}
/**
 * Wallet info returned by list operations
 */
export interface WalletInfo {
    nickname: string;
    type: WalletBackendType;
    address: Address;
    chains: string[];
    isDefault: boolean;
    /** Solana address (if wallet has one, e.g., Bankr) */
    solanaAddress?: string;
}
/**
 * Wallet backend interface
 * Different implementations for different sources
 */
export interface IWalletBackend {
    readonly type: WalletBackendType;
    readonly nickname: string;
    readonly supportedChains: readonly string[];
    /**
     * Get the wallet address
     */
    getAddress(): Promise<Address>;
    /**
     * Check if this wallet supports a specific chain
     */
    supportsChain(chainId: string): boolean;
    /**
     * Get private key (for local/env wallets)
     * Returns undefined for Bankr (no local key access)
     */
    getPrivateKey?(): Promise<`0x${string}`>;
    /**
     * Send raw transaction via Bankr API
     * Only available for Bankr backend
     */
    sendRawTransaction?(tx: RawTransaction): Promise<Hash>;
    /**
     * Check if backend is ready/configured
     */
    isReady(): Promise<boolean>;
}
/**
 * Wallet configuration from wallets.json
 */
export interface WalletConfig {
    source: WalletBackendType;
    path?: string;
    apiKey?: string;
    apiUrl?: string;
    envVar?: string;
    address?: Address;
    privateKey?: `0x${string}`;
    chains?: string[];
}
/**
 * Wallets config file structure
 */
export interface WalletsConfigFile {
    wallets: Record<string, WalletConfig>;
    default?: string;
}
/**
 * Chain IDs for Bankr submission
 */
export declare const BANKR_CHAIN_IDS: Record<string, number>;
/**
 * Chains supported by Bankr
 */
export declare const BANKR_SUPPORTED_CHAINS: readonly ["ethereum", "polygon", "base"];
/**
 * All SODAX-supported EVM chains
 * NOTE: Keep in sync with SODAX SDK supported chains
 * Non-EVM chains (solana, sui, stellar, injective) are excluded
 */
export declare const SODAX_SUPPORTED_CHAINS: readonly ["ethereum", "base", "polygon", "arbitrum", "optimism", "sonic", "avalanche", "bsc", "lightlink", "hyper", "kaia"];
/**
 * SODAX to simple chain ID mapping
 * SODAX uses prefixed format: 0x2105.base, 0x89.polygon
 * Simple format: base, polygon, ethereum
 */
export declare const SODAX_TO_SIMPLE_CHAIN: Record<string, string>;
/**
 * Simple to SODAX chain ID mapping
 */
export declare const SIMPLE_TO_SODAX_CHAIN: Record<string, string>;
/**
 * Normalize chain ID to simple format (base, polygon, ethereum)
 * Handles both SODAX prefixed format and simple format
 */
export declare function normalizeChainId(chainId: string): string;
/**
 * Convert simple chain ID to SODAX format
 */
export declare function toSodaxChainId(chainId: string): string;
/**
 * Check if two chain IDs refer to the same chain
 * Handles format differences between SODAX and simple
 */
export declare function isSameChain(chainId1: string, chainId2: string): boolean;
/**
 * Check if a chain is supported by Bankr
 * Handles both SODAX and simple chain ID formats
 */
export declare function isBankrSupportedChain(chainId: string): boolean;
/**
 * Get numeric chain ID for Bankr
 * Handles both SODAX and simple chain ID formats
 */
export declare function getBankrChainId(chainId: string): number;
//# sourceMappingURL=types.d.ts.map