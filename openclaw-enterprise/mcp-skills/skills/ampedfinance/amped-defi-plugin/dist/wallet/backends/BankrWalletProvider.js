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
import { createPublicClient, http } from 'viem';
import { mainnet, polygon, base } from 'viem/chains';
/**
 * Chain configurations for Bankr
 */
const BANKR_CHAINS = {
    1: { chain: mainnet, name: 'ethereum' },
    137: { chain: polygon, name: 'polygon' },
    8453: { chain: base, name: 'base' },
};
/**
 * Bankr Wallet Provider
 *
 * Implements IEvmWalletProvider for use with SODAX SDK's SpokeProvider.
 * Transactions are signed and broadcast via Bankr's Agent API.
 */
export class BankrWalletProvider {
    publicClient;
    apiUrl;
    apiKey;
    chainId;
    cachedAddress;
    // Polling configuration
    pollIntervalMs = 2000;
    maxPollAttempts = 150; // 5 minutes max
    constructor(config) {
        this.apiKey = config.apiKey;
        this.apiUrl = config.apiUrl || 'https://api.bankr.bot';
        this.chainId = config.chainId;
        this.cachedAddress = config.cachedAddress || null;
        // Validate chain support
        const chainConfig = BANKR_CHAINS[config.chainId];
        if (!chainConfig) {
            throw new Error(`Bankr does not support chainId ${config.chainId}. ` +
                `Supported: Ethereum (1), Polygon (137), Base (8453)`);
        }
        // Create public client for read operations
        this.publicClient = createPublicClient({
            chain: chainConfig.chain,
            transport: http(config.rpcUrl),
        });
        console.log(`[BankrWalletProvider] Initialized for ${chainConfig.name} (${config.chainId})`);
    }
    /**
     * Get the Bankr wallet address
     */
    async getWalletAddress() {
        if (this.cachedAddress)
            return this.cachedAddress;
        console.log('[BankrWalletProvider] Fetching wallet address from Bankr...');
        try {
            const response = await this.submitAndWait('What is my EVM wallet address?');
            // Extract address from response
            const addressMatch = response.match(/0x[a-fA-F0-9]{40}/);
            if (!addressMatch) {
                throw new Error('Could not parse wallet address from Bankr response');
            }
            this.cachedAddress = addressMatch[0];
            console.log(`[BankrWalletProvider] Wallet address: ${this.cachedAddress}`);
            return this.cachedAddress;
        }
        catch (error) {
            console.error('[BankrWalletProvider] Failed to get address:', error);
            throw error;
        }
    }
    /**
     * Send a transaction via Bankr
     *
     * This is the key method - it receives raw transaction data from SODAX SDK
     * and submits it to Bankr for signing and broadcasting.
     */
    async sendTransaction(evmRawTx) {
        console.log('[BankrWalletProvider] Sending transaction via Bankr');
        console.log(`[BankrWalletProvider] To: ${evmRawTx.to}`);
        console.log(`[BankrWalletProvider] Value: ${evmRawTx.value}`);
        console.log(`[BankrWalletProvider] Data: ${evmRawTx.data.slice(0, 20)}...`);
        // Format transaction for Bankr's arbitrary transaction endpoint
        const txJson = JSON.stringify({
            to: evmRawTx.to,
            data: evmRawTx.data,
            value: evmRawTx.value.toString(),
            chainId: this.chainId,
        }, null, 2);
        // Use the documented prompt format
        const prompt = `Submit this transaction:
${txJson}`;
        console.log('[BankrWalletProvider] Submitting to Bankr API...');
        const result = await this.submitAndWaitForJob(prompt);
        // Extract transaction hash from response
        const txHash = this.extractTransactionHash(result);
        if (!txHash) {
            const errorMsg = result.error || result.response || 'Unknown error';
            throw new Error(`Transaction failed: ${errorMsg}`);
        }
        console.log(`[BankrWalletProvider] Transaction hash: ${txHash}`);
        return txHash;
    }
    /**
     * Wait for transaction receipt
     *
     * Uses the public client to query the blockchain directly.
     */
    async waitForTransactionReceipt(txHash) {
        console.log(`[BankrWalletProvider] Waiting for receipt: ${txHash}`);
        const receipt = await this.publicClient.waitForTransactionReceipt({
            hash: txHash,
            timeout: 120_000, // 2 minutes
        });
        // Convert viem receipt to SODAX format
        return {
            transactionHash: receipt.transactionHash,
            transactionIndex: `0x${receipt.transactionIndex.toString(16)}`,
            blockHash: receipt.blockHash,
            blockNumber: `0x${receipt.blockNumber.toString(16)}`,
            from: receipt.from,
            to: receipt.to,
            cumulativeGasUsed: `0x${receipt.cumulativeGasUsed.toString(16)}`,
            gasUsed: `0x${receipt.gasUsed.toString(16)}`,
            contractAddress: receipt.contractAddress,
            logs: receipt.logs.map(log => ({
                address: log.address,
                topics: log.topics || [],
                data: log.data,
                blockHash: log.blockHash,
                blockNumber: log.blockNumber ? `0x${log.blockNumber.toString(16)}` : null,
                logIndex: log.logIndex !== null ? `0x${log.logIndex.toString(16)}` : null,
                transactionHash: log.transactionHash,
                transactionIndex: log.transactionIndex !== null ? `0x${log.transactionIndex.toString(16)}` : null,
                removed: log.removed,
            })),
            logsBloom: receipt.logsBloom,
            status: receipt.status === 'success' ? '0x1' : '0x0',
            type: receipt.type,
            effectiveGasPrice: receipt.effectiveGasPrice ? `0x${receipt.effectiveGasPrice.toString(16)}` : undefined,
        };
    }
    /**
     * Submit prompt and wait for text response
     */
    async submitAndWait(prompt) {
        const result = await this.submitAndWaitForJob(prompt);
        return result.response || '';
    }
    /**
     * Submit prompt and wait for job completion
     */
    async submitAndWaitForJob(prompt) {
        // Submit job
        const submitResponse = await fetch(`${this.apiUrl}/agent/prompt`, {
            method: 'POST',
            headers: {
                'X-API-Key': this.apiKey,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt }),
        });
        if (!submitResponse.ok) {
            const error = await submitResponse.text();
            throw new Error(`Failed to submit job: ${submitResponse.status} ${error}`);
        }
        const submitData = await submitResponse.json();
        if (!submitData.success || !submitData.jobId) {
            throw new Error(`Invalid job response: ${JSON.stringify(submitData)}`);
        }
        const jobId = submitData.jobId;
        console.log(`[BankrWalletProvider] Job submitted: ${jobId}`);
        // Poll for completion
        let lastStatus = '';
        for (let attempt = 0; attempt < this.maxPollAttempts; attempt++) {
            await this.sleep(this.pollIntervalMs);
            const statusResponse = await fetch(`${this.apiUrl}/agent/job/${jobId}`, {
                method: 'GET',
                headers: { 'X-API-Key': this.apiKey },
            });
            if (!statusResponse.ok) {
                const error = await statusResponse.text();
                throw new Error(`Failed to get job status: ${statusResponse.status} ${error}`);
            }
            const result = await statusResponse.json();
            // Log status changes
            if (result.status !== lastStatus) {
                console.log(`[BankrWalletProvider] Job ${jobId}: ${result.status}`);
                lastStatus = result.status;
            }
            // Check terminal states
            switch (result.status) {
                case 'completed':
                    return result;
                case 'failed':
                    throw new Error(`Job failed: ${result.error || 'Unknown error'}`);
                case 'cancelled':
                    throw new Error(`Job was cancelled`);
            }
        }
        throw new Error(`Job ${jobId} timed out`);
    }
    /**
     * Extract transaction hash from Bankr response
     */
    extractTransactionHash(result) {
        // Check richData for transaction info
        if (result.richData) {
            for (const item of result.richData) {
                if (item.transactionHash)
                    return item.transactionHash;
                if (item.txHash)
                    return item.txHash;
                if (item.hash)
                    return item.hash;
            }
        }
        // Try to extract from response text
        if (result.response) {
            // Look for 0x + 64 hex chars
            const hashMatch = result.response.match(/0x[a-fA-F0-9]{64}/);
            if (hashMatch)
                return hashMatch[0];
        }
        return null;
    }
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
/**
 * Create a BankrWalletProvider
 */
export function createBankrWalletProvider(config) {
    return new BankrWalletProvider(config);
}
//# sourceMappingURL=BankrWalletProvider.js.map