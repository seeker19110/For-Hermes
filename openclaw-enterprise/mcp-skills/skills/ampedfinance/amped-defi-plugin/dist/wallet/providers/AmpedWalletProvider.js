/**
 * Amped Wallet Provider
 *
 * Custom wallet provider implementing IEvmWalletProvider from @sodax/types.
 *
 * This replaces wallet-sdk-core's EvmWalletProvider with a more flexible
 * implementation that:
 * 1. Supports all chains including LightLink and HyperEVM
 * 2. Has pluggable backends (local keys, Bankr, etc.)
 * 3. Provides a unified interface for the SODAX SDK
 *
 * Architecture:
 * \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
 * \u2502       AmpedWalletProvider               \u2502
 * \u2502  (implements IEvmWalletProvider)        \u2502
 * \u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
 * \u2502  - SDK-compatible interface             \u2502
 * \u2502  - Chain resolution (all chains)        \u2502
 * \u2502  - Transaction formatting               \u2502
 * \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u252c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
 *                 \u2502
 *         \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
 *         \u25bc               \u25bc
 * \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510 \u250c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510
 * \u2502 LocalKeyBack. \u2502 \u2502 BankrBackend  \u2502
 * \u2502 (evm-wallet)  \u2502 \u2502 (API calls)   \u2502
 * \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518 \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518
 */
import { createPublicClient, http, } from 'viem';
import { createLocalKeyBackend } from './LocalKeyBackend';
import { createBankrBackend } from './BankrBackend';
import { getViemChain, getDefaultRpcUrl, resolveChainId } from './chainConfig';
/**
 * Amped Wallet Provider
 *
 * A drop-in replacement for wallet-sdk-core's EvmWalletProvider
 * that supports all SODAX chains including LightLink and HyperEVM.
 */
export class AmpedWalletProvider {
    publicClient;
    backend;
    chainId;
    constructor(backend, publicClient) {
        this.backend = backend;
        this.publicClient = publicClient;
        this.chainId = backend.getChainId();
        console.log(`[AmpedWalletProvider] Initialized with ${backend.type} backend`);
        console.log(`[AmpedWalletProvider] Chain ID: ${this.chainId}`);
    }
    /**
     * Create an AmpedWalletProvider with a local key backend
     *
     * @param config - Configuration matching EvmWalletProvider's PrivateKeyEvmWalletConfig
     * @returns AmpedWalletProvider instance
     */
    static async fromPrivateKey(config) {
        const chainId = resolveChainId(config.chainId);
        const rpcUrl = config.rpcUrl || getDefaultRpcUrl(chainId);
        const chain = getViemChain(chainId);
        // Create backend
        const backend = await createLocalKeyBackend({
            type: 'localKey',
            privateKey: config.privateKey,
            chainId: config.chainId,
            rpcUrl,
        });
        // Use the backend's public client
        const publicClient = backend.getPublicClient();
        return new AmpedWalletProvider(backend, publicClient);
    }
    /**
     * Create an AmpedWalletProvider with a Bankr backend
     *
     * @param config - Bankr backend configuration
     * @returns AmpedWalletProvider instance
     */
    static async fromBankr(config) {
        const chainId = resolveChainId(config.chainId);
        const rpcUrl = config.rpcUrl || getDefaultRpcUrl(chainId);
        const chain = getViemChain(chainId);
        // Create backend
        const backend = await createBankrBackend({
            type: 'bankr',
            bankrApiUrl: config.bankrApiUrl,
            bankrApiKey: config.bankrApiKey,
            userAddress: config.userAddress,
            chainId: config.chainId,
            rpcUrl,
            policy: config.policy,
        });
        // Create public client (for read operations)
        // Bankr backend doesn't have its own public client
        const publicClient = createPublicClient({
            chain,
            transport: http(rpcUrl),
        }); // Type cast needed due to viem's strict typing
        return new AmpedWalletProvider(backend, publicClient);
    }
    /**
     * Create from generic backend configuration
     */
    static async fromConfig(config) {
        switch (config.type) {
            case 'localKey':
                return AmpedWalletProvider.fromPrivateKey({
                    privateKey: config.privateKey,
                    chainId: config.chainId,
                    rpcUrl: config.rpcUrl,
                });
            case 'bankr':
                const bankrConfig = config;
                return AmpedWalletProvider.fromBankr({
                    bankrApiUrl: bankrConfig.bankrApiUrl,
                    bankrApiKey: bankrConfig.bankrApiKey,
                    userAddress: bankrConfig.userAddress,
                    chainId: config.chainId,
                    rpcUrl: config.rpcUrl,
                    policy: bankrConfig.policy,
                });
            default:
                throw new Error(`Unsupported backend type: ${config.type}`);
        }
    }
    // ===== IEvmWalletProvider Implementation =====
    /**
     * Get the wallet address
     */
    async getWalletAddress() {
        return this.backend.getAddress();
    }
    /**
     * Send a transaction
     *
     * Converts SDK's EvmRawTransaction format to internal format
     * and delegates to the backend.
     */
    async sendTransaction(evmRawTx) {
        console.log(`[AmpedWalletProvider] sendTransaction`);
        console.log(`[AmpedWalletProvider] From: ${evmRawTx.from}`);
        console.log(`[AmpedWalletProvider] To: ${evmRawTx.to}`);
        console.log(`[AmpedWalletProvider] Value: ${evmRawTx.value}`);
        return this.backend.sendTransaction({
            to: evmRawTx.to,
            value: evmRawTx.value,
            data: evmRawTx.data,
        });
    }
    /**
     * Wait for transaction receipt
     *
     * Converts internal receipt format to SDK's EvmRawTransactionReceipt format.
     */
    async waitForTransactionReceipt(txHash) {
        console.log(`[AmpedWalletProvider] waitForTransactionReceipt: ${txHash}`);
        const receipt = await this.backend.waitForTransaction(txHash);
        // Convert to SDK format
        return {
            transactionHash: receipt.transactionHash,
            transactionIndex: '0x0', // Not tracked in our simplified receipt
            blockHash: receipt.blockHash,
            blockNumber: `0x${receipt.blockNumber.toString(16)}`,
            from: receipt.from,
            to: receipt.to,
            cumulativeGasUsed: '0x0', // Not tracked
            gasUsed: `0x${receipt.gasUsed.toString(16)}`,
            contractAddress: null, // Would need to check if this was a deployment
            logs: receipt.logs.map(log => ({
                address: log.address,
                topics: log.topics,
                data: log.data,
                blockHash: receipt.blockHash,
                blockNumber: `0x${receipt.blockNumber.toString(16)}`,
                logIndex: '0x0',
                transactionHash: receipt.transactionHash,
                transactionIndex: '0x0',
                removed: false,
            })),
            logsBloom: '0x',
            status: receipt.status === 'success' ? '0x1' : '0x0',
        };
    }
    // ===== IAmpedWalletProvider Extensions =====
    /**
     * Get the underlying backend
     */
    getBackend() {
        return this.backend;
    }
    /**
     * Get the backend type
     */
    getBackendType() {
        return this.backend.type;
    }
    /**
     * Check if ready for transactions
     */
    async isReady() {
        return this.backend.isReady();
    }
    /**
     * Get chain ID
     */
    getChainId() {
        return this.chainId;
    }
}
//# sourceMappingURL=AmpedWalletProvider.js.map