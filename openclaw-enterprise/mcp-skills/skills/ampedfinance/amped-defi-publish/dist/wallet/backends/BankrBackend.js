/**
 * Bankr Backend - Transaction Execution via Bankr API
 *
 * Submits raw transactions to Bankr's Agent API using the
 * arbitrary transaction format documented at:
 * https://github.com/BankrBot/openclaw-skills/blob/main/bankr/references/arbitrary-transaction.md
 *
 * Supported chains: Ethereum (1), Polygon (137), Base (8453)
 */
import { BANKR_SUPPORTED_CHAINS, isBankrSupportedChain } from '../types';
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
/**
 * Disk cache path for bankr address
 */
const BANKR_CACHE_DIR = join(homedir(), '.openclaw', 'cache');
const getBankrCachePath = (nickname) => join(BANKR_CACHE_DIR, `bankr-${nickname}-address.json`);
/**
 * Bankr wallet backend
 * Submits raw transactions via Bankr Agent API
 */
export class BankrBackend {
    type = 'bankr';
    nickname;
    supportedChains = BANKR_SUPPORTED_CHAINS;
    apiUrl;
    apiKey;
    cachedAddress = null;
    cachedSolanaAddress = null;
    // Polling configuration
    pollIntervalMs = 2000;
    maxPollAttempts = 150; // 5 minutes max
    constructor(config) {
        this.nickname = config.nickname || 'bankr';
        this.apiUrl = config.apiUrl || 'https://api.bankr.bot';
        this.apiKey = config.apiKey;
        // Try to load cached address from disk
        this.loadCachedAddress();
        console.log(`[BankrBackend] Initialized as "${this.nickname}"`);
        console.log(`[BankrBackend] Supported chains: ${this.supportedChains.join(', ')}`);
        if (this.cachedAddress) {
            console.log(`[BankrBackend] Loaded cached address: ${this.cachedAddress}`);
        }
    }
    /**
     * Load cached address from disk
     */
    loadCachedAddress() {
        const cachePath = getBankrCachePath(this.nickname);
        if (existsSync(cachePath)) {
            try {
                const data = JSON.parse(readFileSync(cachePath, 'utf-8'));
                if (data.address && data.address.match(/^0x[a-fA-F0-9]{40}$/)) {
                    this.cachedAddress = data.address;
                }
            }
            catch (e) {
                console.warn(`[BankrBackend] Failed to load cached address: ${e}`);
            }
        }
    }
    /**
     * Save address to disk cache
     */
    saveCachedAddress(address) {
        const cachePath = getBankrCachePath(this.nickname);
        try {
            if (!existsSync(BANKR_CACHE_DIR)) {
                mkdirSync(BANKR_CACHE_DIR, { recursive: true });
            }
            writeFileSync(cachePath, JSON.stringify({ address, timestamp: Date.now() }));
            console.log(`[BankrBackend] Cached address to ${cachePath}`);
        }
        catch (e) {
            console.warn(`[BankrBackend] Failed to cache address: ${e}`);
        }
    }
    async getAddress() {
        if (this.cachedAddress)
            return this.cachedAddress;
        // Query Bankr for the wallet address
        console.log('[BankrBackend] Fetching wallet address from Bankr...');
        try {
            const response = await this.submitAndWait('What is my EVM wallet address?');
            // Extract address from response
            const addressMatch = response.match(/0x[a-fA-F0-9]{40}/);
            if (!addressMatch) {
                console.warn('[BankrBackend] Could not parse address from response:', response.slice(0, 100));
                throw new Error('[BankrBackend] Could not determine wallet address from Bankr');
            }
            this.cachedAddress = addressMatch[0];
            // Save to disk for next time
            this.saveCachedAddress(this.cachedAddress);
            console.log(`[BankrBackend] Wallet address: ${this.cachedAddress}`);
            return this.cachedAddress;
        }
        catch (error) {
            console.error('[BankrBackend] Failed to get address:', error);
            throw error;
        }
    }
    /**
     * Get the Solana wallet address from Bankr
     */
    async getSolanaAddress() {
        if (this.cachedSolanaAddress)
            return this.cachedSolanaAddress;
        // Check for cached address on disk
        const cachePath = `${process.env.HOME}/.openclaw/cache/bankr-${this.nickname}-solana-address.json`;
        try {
            const fs = await import('fs');
            if (fs.existsSync(cachePath)) {
                const cached = JSON.parse(fs.readFileSync(cachePath, 'utf8'));
                if (cached.address && Date.now() - cached.timestamp < 86400000) {
                    this.cachedSolanaAddress = cached.address;
                    console.log(`[BankrBackend] Loaded cached Solana address: ${this.cachedSolanaAddress}`);
                    return this.cachedSolanaAddress;
                }
            }
        }
        catch (e) {
            // Cache miss, continue to query
        }
        console.log('[BankrBackend] Fetching Solana wallet address from Bankr...');
        try {
            const response = await this.submitAndWait('What is my Solana wallet address?');
            // Solana addresses are base58, typically 32-44 chars, no 0x prefix
            const solanaMatch = response.match(/[1-9A-HJ-NP-Za-km-z]{32,44}/);
            if (!solanaMatch) {
                console.warn('[BankrBackend] Could not parse Solana address from response');
                return null;
            }
            this.cachedSolanaAddress = solanaMatch[0];
            console.log(`[BankrBackend] Solana address: ${this.cachedSolanaAddress}`);
            // Cache to disk
            try {
                const fs = await import('fs');
                const path = await import('path');
                const cacheDir = path.dirname(cachePath);
                if (!fs.existsSync(cacheDir))
                    fs.mkdirSync(cacheDir, { recursive: true });
                fs.writeFileSync(cachePath, JSON.stringify({ address: this.cachedSolanaAddress, timestamp: Date.now() }));
            }
            catch (e) {
                console.warn('[BankrBackend] Failed to cache Solana address:', e);
            }
            return this.cachedSolanaAddress;
        }
        catch (error) {
            console.error('[BankrBackend] Failed to get Solana address:', error);
            return null;
        }
    }
    supportsChain(chainId) {
        // Normalize chain ID to handle SODAX format (0x2105.base -> base)
        return isBankrSupportedChain(chainId);
    }
    async isReady() {
        if (!this.apiKey)
            return false;
        try {
            // Test API connectivity
            const response = await fetch(`${this.apiUrl}/agent/prompt`, {
                method: 'POST',
                headers: {
                    'X-API-Key': this.apiKey,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: 'ping' }),
            });
            return response.status !== 503 && response.status !== 502;
        }
        catch {
            return false;
        }
    }
    /**
     * Send raw transaction via Bankr
     * Uses the arbitrary transaction format
     */
    async sendRawTransaction(tx) {
        console.log(`[BankrBackend] Sending raw transaction`);
        console.log(`[BankrBackend] To: ${tx.to}`);
        console.log(`[BankrBackend] Chain: ${tx.chainId}`);
        console.log(`[BankrBackend] Value: ${tx.value}`);
        console.log(`[BankrBackend] Data: ${tx.data.slice(0, 20)}...`);
        // Format as documented in arbitrary-transaction.md
        const txJson = JSON.stringify({
            to: tx.to,
            data: tx.data,
            value: tx.value,
            chainId: tx.chainId,
        }, null, 2);
        // Use the documented prompt format
        const prompt = `Submit this transaction:
${txJson}`;
        console.log(`[BankrBackend] Submitting to Bankr API...`);
        const result = await this.submitAndWaitForJob(prompt);
        // Extract transaction hash from response
        const txHash = this.extractTransactionHash(result);
        if (!txHash) {
            const errorMsg = result.error || result.response || 'Unknown error';
            throw new Error(`[BankrBackend] Transaction failed: ${errorMsg}`);
        }
        console.log(`[BankrBackend] Transaction hash: ${txHash}`);
        return txHash;
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
            throw new Error(`[BankrBackend] Failed to submit job: ${submitResponse.status} ${error}`);
        }
        const submitData = await submitResponse.json();
        if (!submitData.success || !submitData.jobId) {
            throw new Error(`[BankrBackend] Invalid job response: ${JSON.stringify(submitData)}`);
        }
        const jobId = submitData.jobId;
        console.log(`[BankrBackend] Job submitted: ${jobId}`);
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
                throw new Error(`[BankrBackend] Failed to get job status: ${statusResponse.status} ${error}`);
            }
            const result = await statusResponse.json();
            // Log status changes
            if (result.status !== lastStatus) {
                console.log(`[BankrBackend] Job ${jobId}: ${result.status}`);
                lastStatus = result.status;
            }
            // Log progress updates
            if (result.statusUpdates && result.statusUpdates.length > 0) {
                const lastUpdate = result.statusUpdates[result.statusUpdates.length - 1];
                console.log(`[BankrBackend] Progress: ${lastUpdate.message}`);
            }
            // Check terminal states
            switch (result.status) {
                case 'completed':
                    return result;
                case 'failed':
                    throw new Error(`[BankrBackend] Job failed: ${result.error || 'Unknown error'}`);
                case 'cancelled':
                    throw new Error(`[BankrBackend] Job was cancelled`);
            }
        }
        throw new Error(`[BankrBackend] Job ${jobId} timed out`);
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
            // Check for failure indicators
            if (result.response.toLowerCase().includes('reverted') ||
                result.response.toLowerCase().includes('failed') ||
                result.response.toLowerCase().includes('insufficient')) {
                console.error(`[BankrBackend] Transaction failed: ${result.response}`);
                return null;
            }
        }
        return null;
    }
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
/**
 * Create a Bankr backend from API key
 */
export function createBankrBackend(config) {
    return new BankrBackend(config);
}
//# sourceMappingURL=BankrBackend.js.map