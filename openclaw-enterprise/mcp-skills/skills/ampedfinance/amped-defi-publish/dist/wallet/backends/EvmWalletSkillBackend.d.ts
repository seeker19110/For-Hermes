/**
 * EVM Wallet Skill Backend
 *
 * Loads wallet from ~/.evm-wallet.json (created by evm-wallet-skill)
 */
import type { Address } from 'viem';
import type { IWalletBackend } from '../types';
/**
 * Backend for evm-wallet-skill wallets
 * Supports all SODAX chains (local key signing)
 */
export declare class EvmWalletSkillBackend implements IWalletBackend {
    readonly type: "evm-wallet-skill";
    readonly nickname: string;
    readonly supportedChains: readonly string[];
    private walletPath;
    private cachedWallet;
    constructor(options: {
        nickname: string;
        path?: string;
        chains?: string[];
    });
    /**
     * Load wallet from file (cached)
     */
    private loadWallet;
    getAddress(): Promise<Address>;
    supportsChain(chainId: string): boolean;
    getPrivateKey(): Promise<`0x${string}`>;
    isReady(): Promise<boolean>;
}
/**
 * Create an evm-wallet-skill backend
 */
export declare function createEvmWalletSkillBackend(options?: {
    nickname?: string;
    path?: string;
    chains?: string[];
}): EvmWalletSkillBackend;
//# sourceMappingURL=EvmWalletSkillBackend.d.ts.map