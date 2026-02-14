/**
 * Bankr Wallet Provider for SODAX SDK
 *
 * Implements IEvmWalletProvider interface to allow SODAX SDK
 * to execute transactions through Bankr's API.
 *
 * Instead of signing locally, transactions are submitted to Bankr
 * which signs and broadcasts them server-side.
 *
 * Supported chains: Ethereum (1), Polygon (137), Base (8453)
 */
import type { Address, Hash, PublicClient } from 'viem';
import type { IEvmWalletProvider, EvmRawTransaction, EvmRawTransactionReceipt } from '@sodax/types';
/**
 * Configuration for BankrWalletProvider
 */
export interface BankrWalletProviderConfig {
    apiKey: string;
    apiUrl?: string;
    chainId: number;
    rpcUrl?: string;
    /** Pre-cached address (avoids initial API call) */
    cachedAddress?: Address;
}
/**
 * Bankr Wallet Provider
 *
 * Implements IEvmWalletProvider for use with SODAX SDK's SpokeProvider.
 * Transactions are signed and broadcast via Bankr's Agent API.
 */
export declare class BankrWalletProvider implements IEvmWalletProvider {
    readonly publicClient: PublicClient;
    private readonly apiUrl;
    private readonly apiKey;
    private readonly chainId;
    private cachedAddress;
    private readonly pollIntervalMs;
    private readonly maxPollAttempts;
    constructor(config: BankrWalletProviderConfig);
    /**
     * Get the Bankr wallet address
     */
    getWalletAddress(): Promise<Address>;
    /**
     * Send a transaction via Bankr
     *
     * This is the key method - it receives raw transaction data from SODAX SDK
     * and submits it to Bankr for signing and broadcasting.
     */
    sendTransaction(evmRawTx: EvmRawTransaction): Promise<Hash>;
    /**
     * Wait for transaction receipt
     *
     * Uses the public client to query the blockchain directly.
     */
    waitForTransactionReceipt(txHash: Hash): Promise<EvmRawTransactionReceipt>;
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
 * Create a BankrWalletProvider
 */
export declare function createBankrWalletProvider(config: BankrWalletProviderConfig): BankrWalletProvider;
//# sourceMappingURL=BankrWalletProvider.d.ts.map