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
import { createPublicClient, type Hash, type Address } from 'viem';
import type { EvmRawTransaction, EvmRawTransactionReceipt } from '@sodax/types';
import type { IWalletBackend, WalletBackendConfig, WalletBackendType, IAmpedWalletProvider, BankrBackendConfig } from './types';
/**
 * Amped Wallet Provider
 *
 * A drop-in replacement for wallet-sdk-core's EvmWalletProvider
 * that supports all SODAX chains including LightLink and HyperEVM.
 */
export declare class AmpedWalletProvider implements IAmpedWalletProvider {
    readonly publicClient: ReturnType<typeof createPublicClient>;
    private readonly backend;
    private readonly chainId;
    private constructor();
    /**
     * Create an AmpedWalletProvider with a local key backend
     *
     * @param config - Configuration matching EvmWalletProvider's PrivateKeyEvmWalletConfig
     * @returns AmpedWalletProvider instance
     */
    static fromPrivateKey(config: {
        privateKey: `0x${string}`;
        chainId: string | number;
        rpcUrl?: string;
    }): Promise<AmpedWalletProvider>;
    /**
     * Create an AmpedWalletProvider with a Bankr backend
     *
     * @param config - Bankr backend configuration
     * @returns AmpedWalletProvider instance
     */
    static fromBankr(config: {
        bankrApiUrl: string;
        bankrApiKey: string;
        userAddress: Address;
        chainId: string | number;
        rpcUrl?: string;
        policy?: BankrBackendConfig['policy'];
    }): Promise<AmpedWalletProvider>;
    /**
     * Create from generic backend configuration
     */
    static fromConfig(config: WalletBackendConfig): Promise<AmpedWalletProvider>;
    /**
     * Get the wallet address
     */
    getWalletAddress(): Promise<Address>;
    /**
     * Send a transaction
     *
     * Converts SDK's EvmRawTransaction format to internal format
     * and delegates to the backend.
     */
    sendTransaction(evmRawTx: EvmRawTransaction): Promise<Hash>;
    /**
     * Wait for transaction receipt
     *
     * Converts internal receipt format to SDK's EvmRawTransactionReceipt format.
     */
    waitForTransactionReceipt(txHash: Hash): Promise<EvmRawTransactionReceipt>;
    /**
     * Get the underlying backend
     */
    getBackend(): IWalletBackend;
    /**
     * Get the backend type
     */
    getBackendType(): WalletBackendType;
    /**
     * Check if ready for transactions
     */
    isReady(): Promise<boolean>;
    /**
     * Get chain ID
     */
    getChainId(): number;
}
export type { IAmpedWalletProvider };
//# sourceMappingURL=AmpedWalletProvider.d.ts.map