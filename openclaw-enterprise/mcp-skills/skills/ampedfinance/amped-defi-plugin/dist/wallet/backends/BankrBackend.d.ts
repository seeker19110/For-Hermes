/**
 * Bankr Backend - Transaction Execution via Bankr API
 *
 * Submits raw transactions to Bankr's Agent API using the
 * arbitrary transaction format documented at:
 * https://github.com/BankrBot/openclaw-skills/blob/main/bankr/references/arbitrary-transaction.md
 *
 * Supported chains: Ethereum (1), Polygon (137), Base (8453)
 */
import type { Address, Hash } from 'viem';
import type { IWalletBackend, RawTransaction } from '../types';
/**
 * Bankr backend configuration
 */
export interface BankrBackendConfig {
    nickname?: string;
    apiKey: string;
    apiUrl?: string;
}
/**
 * Bankr wallet backend
 * Submits raw transactions via Bankr Agent API
 */
export declare class BankrBackend implements IWalletBackend {
    readonly type: "bankr";
    readonly nickname: string;
    readonly supportedChains: readonly ["ethereum", "polygon", "base"];
    private readonly apiUrl;
    private readonly apiKey;
    private cachedAddress;
    private cachedSolanaAddress;
    private readonly pollIntervalMs;
    private readonly maxPollAttempts;
    constructor(config: BankrBackendConfig);
    /**
     * Load cached address from disk
     */
    private loadCachedAddress;
    /**
     * Save address to disk cache
     */
    private saveCachedAddress;
    getAddress(): Promise<Address>;
    /**
     * Get the Solana wallet address from Bankr
     */
    getSolanaAddress(): Promise<string | null>;
    supportsChain(chainId: string): boolean;
    isReady(): Promise<boolean>;
    /**
     * Send raw transaction via Bankr
     * Uses the arbitrary transaction format
     */
    sendRawTransaction(tx: RawTransaction): Promise<Hash>;
    /**
     * Submit prompt and wait for text response
     */
    private submitAndWait;
    /**
     * Submit prompt and wait for job completion
     */
    private submitAndWaitForJob;
    /**
     * Extract transaction hash from Bankr response
     */
    private extractTransactionHash;
    private sleep;
}
/**
 * Create a Bankr backend from API key
 */
export declare function createBankrBackend(config: BankrBackendConfig): BankrBackend;
//# sourceMappingURL=BankrBackend.d.ts.map