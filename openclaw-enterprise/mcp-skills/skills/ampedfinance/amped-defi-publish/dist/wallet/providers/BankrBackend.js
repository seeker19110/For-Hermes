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
import { resolveChainId } from './chainConfig';
/**
 * Serialize error objects for readable error messages
 */
function serializeError(error) {
    if (error instanceof Error)
        return error.message;
    if (typeof error === 'string')
        return error;
    try {
        return JSON.stringify(error, (k, v) => typeof v === 'bigint' ? v.toString() : v, 2);
    }
    catch {
        return String(error);
    }
}
/**
 * Chain ID to chain name mapping for Bankr prompts
 */
const CHAIN_NAMES = {
    1: 'ethereum',
    8453: 'base',
    137: 'polygon',
    42161: 'arbitrum',
    10: 'optimism',
    1890: 'lightlink',
    146: 'sonic',
};
/**
 * Bankr execution backend
 *
 * Delegates transaction execution to Bankr's Agent API.
 * The agent never has direct access to private keys.
 */
export class BankrBackend {
    type = 'bankr';
    apiUrl;
    apiKey;
    userAddress;
    chainId;
    policy;
    // Polling configuration
    pollIntervalMs = 2000;
    maxPollAttempts = 150; // 5 minutes max
    constructor(config) {
        this.apiUrl = config.bankrApiUrl || 'https://api.bankr.bot';
        this.apiKey = config.bankrApiKey;
        this.userAddress = config.userAddress;
        this.chainId = resolveChainId(config.chainId);
        this.policy = config.policy;
        console.log(`[BankrBackend] Initialized for chain ${this.chainId}`);
        console.log(`[BankrBackend] User address: ${this.userAddress}`);
        console.log(`[BankrBackend] API URL: ${this.apiUrl}`);
    }
    /**
     * Get the wallet address (Bankr-provisioned)
     */
    async getAddress() {
        return this.userAddress;
    }
    /**
     * Send a transaction via Bankr Agent API
     *
     * Formats the transaction as a natural language prompt and submits
     * to Bankr's async job system.
     */
    async sendTransaction(tx) {
        console.log(`[BankrBackend] Sending transaction via Bankr API`);
        console.log(`[BankrBackend] To: ${tx.to}`);
        console.log(`[BankrBackend] Value: ${tx.value || 0n}`);
        console.log(`[BankrBackend] Data: ${tx.data ? tx.data.slice(0, 20) + '...' : '0x'}`);
        // Validate against policy
        if (this.policy) {
            await this.validatePolicy(tx);
        }
        // Format transaction as JSON for Bankr prompt
        const txJson = JSON.stringify({
            to: tx.to,
            data: tx.data || '0x',
            value: (tx.value || 0n).toString(),
            chainId: this.chainId,
        });
        // Create natural language prompt for Bankr
        const prompt = `Submit this transaction: ${txJson}`;
        console.log(`[BankrBackend] Submitting prompt to Bankr API`);
        // Submit job to Bankr
        const jobId = await this.submitJob(prompt);
        console.log(`[BankrBackend] Job submitted: ${jobId}`);
        // Poll for completion
        const result = await this.pollJobUntilComplete(jobId);
        // Extract transaction hash from response
        const txHash = this.extractTransactionHash(result);
        if (!txHash) {
            throw new Error(`[BankrBackend] Transaction failed: ${serializeError(result.response || result.error) || 'Unknown error'}`);
        }
        console.log(`[BankrBackend] Transaction hash: ${txHash}`);
        return txHash;
    }
    /**
     * Wait for transaction confirmation
     *
     * Note: With Bankr, the transaction is already confirmed when we get
     * the response. This method exists for interface compatibility but
     * returns a minimal receipt.
     */
    async waitForTransaction(txHash) {
        console.log(`[BankrBackend] waitForTransaction called for: ${txHash}`);
        // Bankr transactions are confirmed when the job completes
        // We return a minimal receipt since we don't have full details
        return {
            transactionHash: txHash,
            blockNumber: 0n, // Unknown - would need to query chain
            blockHash: '0x0000000000000000000000000000000000000000000000000000000000000000',
            from: this.userAddress,
            to: null,
            gasUsed: 0n,
            status: 'success',
            logs: [],
        };
    }
    /**
     * Check if backend is ready
     *
     * Verifies Bankr API connectivity with a simple balance query.
     */
    async isReady() {
        if (!this.apiUrl || !this.apiKey || !this.userAddress) {
            return false;
        }
        try {
            // Test API connectivity with a simple query
            const response = await fetch(`${this.apiUrl}/agent/prompt`, {
                method: 'POST',
                headers: {
                    'X-API-Key': this.apiKey,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: 'ping' }),
            });
            // Even a 4xx error means API is reachable
            return response.status !== 503 && response.status !== 502;
        }
        catch (error) {
            console.error('[BankrBackend] Connectivity check failed:', error);
            return false;
        }
    }
    /**
     * Get the chain ID
     */
    getChainId() {
        return this.chainId;
    }
    /**
     * Submit a job to Bankr Agent API
     */
    async submitJob(prompt) {
        const response = await fetch(`${this.apiUrl}/agent/prompt`, {
            method: 'POST',
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`[BankrBackend] Failed to submit job: ${response.status} ${error}`);
        }
        const data = await response.json();
        if (!data.success || !data.jobId) {
            throw new Error(`[BankrBackend] Invalid job submission response: ${JSON.stringify(data)}`);
        }
        return data.jobId;
    }
    /**
     * Poll for job completion
     */
    async pollJobUntilComplete(jobId) {
        let lastStatus = '';
        for (let attempt = 0; attempt < this.maxPollAttempts; attempt++) {
            await this.sleep(this.pollIntervalMs);
            const result = await this.getJobStatus(jobId);
            // Log status changes
            if (result.status !== lastStatus) {
                console.log(`[BankrBackend] Job ${jobId} status: ${result.status}`);
                lastStatus = result.status;
            }
            // Log status updates
            if (result.statusUpdates && result.statusUpdates.length > 0) {
                const lastUpdate = result.statusUpdates[result.statusUpdates.length - 1];
                console.log(`[BankrBackend] Progress: ${lastUpdate.message}`);
            }
            // Check for terminal states
            switch (result.status) {
                case 'completed':
                    return result;
                case 'failed':
                    throw new Error(`[BankrBackend] Job failed: ${serializeError(result.error) || 'Unknown error'}`);
                case 'cancelled':
                    throw new Error(`[BankrBackend] Job was cancelled`);
                case 'pending':
                case 'processing':
                    // Continue polling
                    break;
                default:
                    console.warn(`[BankrBackend] Unknown status: ${result.status}`);
            }
        }
        throw new Error(`[BankrBackend] Job ${jobId} timed out after ${this.maxPollAttempts * this.pollIntervalMs / 1000} seconds`);
    }
    /**
     * Get job status from Bankr API
     */
    async getJobStatus(jobId) {
        const response = await fetch(`${this.apiUrl}/agent/job/${jobId}`, {
            method: 'GET',
            headers: {
                'X-API-Key': this.apiKey,
            },
        });
        if (!response.ok) {
            const error = await response.text();
            throw new Error(`[BankrBackend] Failed to get job status: ${response.status} ${error}`);
        }
        return await response.json();
    }
    /**
     * Extract transaction hash from Bankr response
     *
     * The response may contain the tx hash in various formats:
     * - In richData array
     * - In the response text (e.g., "Transaction hash: 0x...")
     */
    extractTransactionHash(result) {
        // Check richData for transaction info
        if (result.richData) {
            for (const item of result.richData) {
                if (item.transactionHash) {
                    return item.transactionHash;
                }
                if (item.txHash) {
                    return item.txHash;
                }
                if (item.hash) {
                    return item.hash;
                }
            }
        }
        // Try to extract from response text
        if (result.response) {
            // Look for hex transaction hash pattern (0x followed by 64 hex chars)
            const hashMatch = result.response.match(/0x[a-fA-F0-9]{64}/);
            if (hashMatch) {
                return hashMatch[0];
            }
            // Check if response indicates failure
            if (result.response.toLowerCase().includes('reverted') ||
                result.response.toLowerCase().includes('failed') ||
                result.response.toLowerCase().includes('insufficient')) {
                console.error(`[BankrBackend] Transaction failed: ${result.response}`);
                return null;
            }
        }
        return null;
    }
    /**
     * Validate transaction against policy
     */
    async validatePolicy(tx) {
        if (!this.policy)
            return;
        // Check max value per transaction
        if (this.policy.maxValuePerTx && tx.value && tx.value > this.policy.maxValuePerTx) {
            throw new Error(`Transaction value ${tx.value} exceeds max allowed ${this.policy.maxValuePerTx}`);
        }
        // Check allowed contracts
        if (this.policy.allowedContracts && this.policy.allowedContracts.length > 0) {
            if (!this.policy.allowedContracts.includes(tx.to)) {
                throw new Error(`Contract ${tx.to} is not in the allowed contracts list`);
            }
        }
    }
    /**
     * Sleep helper
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
/**
 * Create a BankrBackend from configuration
 */
export async function createBankrBackend(config) {
    const backend = new BankrBackend(config);
    // Verify connectivity
    const ready = await backend.isReady();
    if (!ready) {
        console.warn('[BankrBackend] Backend created but connectivity check failed');
    }
    return backend;
}
//# sourceMappingURL=BankrBackend.js.map