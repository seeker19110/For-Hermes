/**
 * Environment Variable Backend
 *
 * Loads wallet from environment variables:
 * - AMPED_OC_WALLETS_JSON: JSON with wallet configs
 * - Or individual env vars for address/privateKey
 */
import type { Address } from 'viem';
import type { IWalletBackend } from '../types';
/**
 * Environment variable backend configuration
 */
export interface EnvBackendConfig {
    nickname: string;
    address?: Address;
    privateKey?: `0x${string}`;
    envVar?: string;
    chains?: string[];
}
/**
 * Environment variable wallet backend
 * Supports all SODAX chains (local key signing)
 */
export declare class EnvBackend implements IWalletBackend {
    readonly type: "env";
    readonly nickname: string;
    readonly supportedChains: readonly string[];
    private address;
    private privateKey;
    private envVar;
    constructor(config: EnvBackendConfig);
    /**
     * Load wallet from environment variable if needed
     */
    private loadFromEnv;
    getAddress(): Promise<Address>;
    supportsChain(chainId: string): boolean;
    getPrivateKey(): Promise<`0x${string}`>;
    isReady(): Promise<boolean>;
}
/**
 * Create env backend from direct config
 */
export declare function createEnvBackend(config: EnvBackendConfig): EnvBackend;
/**
 * Load wallets from AMPED_OC_WALLETS_JSON environment variable
 * Returns multiple backends keyed by wallet name
 */
export declare function loadWalletsFromEnv(): Map<string, EnvBackend>;
//# sourceMappingURL=EnvBackend.d.ts.map