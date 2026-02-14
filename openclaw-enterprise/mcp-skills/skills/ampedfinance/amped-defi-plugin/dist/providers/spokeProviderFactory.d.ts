/**
 * Spoke Provider Factory
 *
 * Creates spoke providers for SODAX operations.
 * Supports both local key signing and Bankr API execution.
 *
 * Flow:
 * 1. Resolve wallet by nickname using WalletManager
 * 2. Check if wallet supports requested chain
 * 3. For local wallets: use SDK's EvmWalletProvider
 * 4. For Bankr wallets: use BankrWalletProvider (submits to Bankr API)
 */
import { type SpokeProvider } from '@sodax/sdk';
/**
 * Get a spoke provider for the given wallet and chain
 * Returns cached provider if available, otherwise creates a new one
 *
 * @param walletId - The wallet identifier/nickname
 * @param chainId - The chain identifier
 * @param raw - If true, still creates full provider (raw mode not yet supported)
 * @returns The spoke provider instance
 */
export declare function getSpokeProvider(walletId: string, chainId: string, raw?: boolean): Promise<SpokeProvider>;
/**
 * Clear the provider cache
 * Useful for testing or when wallet configuration changes
 */
export declare function clearProviderCache(): void;
/**
 * Get cache statistics
 * @returns Object with cache size and keys
 */
export declare function getCacheStats(): {
    size: number;
    keys: string[];
};
export type { SpokeProvider };
//# sourceMappingURL=spokeProviderFactory.d.ts.map