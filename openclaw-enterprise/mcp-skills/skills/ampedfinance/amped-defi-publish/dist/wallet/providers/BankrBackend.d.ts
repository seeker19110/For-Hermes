/**
 * Bankr Backend - Transaction Execution Layer
 *
 * CRITICAL: This backend is for EXECUTION ONLY, not routing.
 *
 * Architecture:
 *   SODAX SDK (routing) → BankrBackend (execution) → Blockchain
 *
 * What Bankr DOES:
 *   ✓ Signs the pre-computed transaction from SODAX
 *   ✓ Submits to blockchain via Bankr API
 *   ✓ Returns transaction hash
 *
 * What Bankr does NOT do:
 *   ✗ NO routing decisions
 *   ✗ NO DeFi protocol selection
 *   ✗ NO swap optimization
 *   ✗ NO interpretation of intent
 *
 * The SODAX SDK always handles routing logic. Bankr receives the exact
 * transaction data (to, data, value, chainId) and submits it verbatim.
 *
 * @see SKILL.md "Transaction Execution Architecture" section
 */
import type { Hash, Address } from 'viem';
import type { IWalletBackend, BankrBackendConfig, TransactionRequest, TransactionReceipt } from './types';
/**
 * Bankr execution backend
 *
 * Delegates transaction execution to Bankr's Agent API.
 * The agent never has direct access to private keys.
 */
export declare class BankrBackend implements IWalletBackend {
    readonly type: "bankr";
    private readonly apiUrl;
    private readonly apiKey;
    private readonly userAddress;
    private readonly chainId;
    private readonly policy?;
    private readonly pollIntervalMs;
    private readonly maxPollAttempts;
    constructor(config: BankrBackendConfig);
    /**
     * Get the wallet address (Bankr-provisioned)
     */
    getAddress(): Promise<Address>;
    /**
     * Send a transaction via Bankr Agent API
     *
     * Formats the transaction as a natural language prompt and submits
     * to Bankr's async job system.
     */
    sendTransaction(tx: TransactionRequest): Promise<Hash>;
    /**
     * Wait for transaction confirmation
     *
     * Note: With Bankr, the transaction is already confirmed when we get
     * the response. This method exists for interface compatibility but
     * returns a minimal receipt.
     */
    waitForTransaction(txHash: Hash): Promise<TransactionReceipt>;
    /**
     * Check if backend is ready
     *
     * Verifies Bankr API connectivity with a simple balance query.
     */
    isReady(): Promise<boolean>;
    /**
     * Get the chain ID
     */
    getChainId(): number;
    /**
     * Submit a job to Bankr Agent API
     */
    private submitJob;
    /**
     * Poll for job completion
     */
    private pollJobUntilComplete;
    /**
     * Get job status from Bankr API
     */
    private getJobStatus;
    /**
     * Extract transaction hash from Bankr response
     *
     * The response may contain the tx hash in various formats:
     * - In richData array
     * - In the response text (e.g., "Transaction hash: 0x...")
     */
    private extractTransactionHash;
    /**
     * Validate transaction against policy
     */
    private validatePolicy;
    /**
     * Sleep helper
     */
    private sleep;
}
/**
 * Create a BankrBackend from configuration
 */
export declare function createBankrBackend(config: BankrBackendConfig): Promise<BankrBackend>;
//# sourceMappingURL=BankrBackend.d.ts.map