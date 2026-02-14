/**
 * Local Key Backend
 *
 * Wallet backend implementation using local private keys.
 * Compatible with evm-wallet-skill's key storage.
 *
 * Uses viem for transaction signing and submission.
 */
import { createPublicClient, createWalletClient, type Hash, type Address } from 'viem';
import type { IWalletBackend, LocalKeyBackendConfig, TransactionRequest, TransactionReceipt } from './types';
/**
 * Local private key wallet backend
 *
 * Signs transactions locally using the provided private key.
 * This is the standard backend for self-custody wallets.
 */
export declare class LocalKeyBackend implements IWalletBackend {
    readonly type: "localKey";
    private readonly account;
    private readonly walletClient;
    private readonly _publicClient;
    private readonly chainId;
    private readonly chain;
    constructor(config: LocalKeyBackendConfig);
    /**
     * Get the wallet address
     */
    getAddress(): Promise<Address>;
    /**
     * Send a transaction
     *
     * Signs locally and submits via RPC.
     */
    sendTransaction(tx: TransactionRequest): Promise<Hash>;
    /**
     * Wait for transaction confirmation
     */
    waitForTransaction(txHash: Hash): Promise<TransactionReceipt>;
    /**
     * Check if backend is ready
     *
     * For local key backend, we verify RPC connectivity.
     */
    isReady(): Promise<boolean>;
    /**
     * Get the chain ID
     */
    getChainId(): number;
    /**
     * Get the public client (for external use)
     */
    getPublicClient(): ReturnType<typeof createPublicClient>;
    /**
     * Get the wallet client (for advanced use cases)
     */
    getWalletClient(): ReturnType<typeof createWalletClient>;
}
/**
 * Create a LocalKeyBackend from configuration
 */
export declare function createLocalKeyBackend(config: LocalKeyBackendConfig): Promise<LocalKeyBackend>;
//# sourceMappingURL=LocalKeyBackend.d.ts.map