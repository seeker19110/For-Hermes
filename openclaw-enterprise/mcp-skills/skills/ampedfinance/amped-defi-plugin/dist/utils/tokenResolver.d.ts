/**
 * Token Resolution Utility
 *
 * Resolves token symbols to addresses using the SODAX SDK config service.
 * Supports case-insensitive symbol lookup with caching.
 * Handles both EVM (0x) and Solana (base58) address formats.
 */
import type { Token } from '@sodax/types';
declare function isSolanaChain(chainId: string): boolean;
/**
 * Check if a string is a valid EVM address (0x format)
 */
declare function isEvmAddress(value: string): boolean;
/**
 * Check if a string is a valid Solana address (base58 format)
 * Solana addresses are 32-44 characters, base58 encoded
 */
declare function isSolanaAddress(value: string): boolean;
/**
 * Check if a string is a valid token address (EVM or Solana)
 */
declare function isValidTokenAddress(value: string, chainId?: string): boolean;
/**
 * Resolve a token symbol or address to a normalized address
 *
 * @param chainId - The chain ID to resolve the token on
 * @param tokenInput - Token symbol (e.g., "USDC") or address
 * @returns The token address (lowercase for EVM, original case for Solana)
 * @throws Error if token symbol is not found on the chain
 */
export declare function resolveToken(chainId: string, tokenInput: string): Promise<string>;
/**
 * Resolve multiple tokens at once (for efficiency)
 *
 * @param chainId - The chain ID
 * @param tokenInputs - Array of token symbols or addresses
 * @returns Array of resolved addresses
 */
export declare function resolveTokens(chainId: string, tokenInputs: string[]): Promise<string[]>;
/**
 * Get token info by symbol or address
 * Returns null if not found
 */
export declare function getTokenInfo(chainId: string, tokenInput: string): Promise<Token | null>;
/**
 * Clear the token cache (useful for testing or after config refresh)
 */
export declare function clearTokenCache(): void;
/**
 * Get all cached tokens for a chain
 */
export declare function getCachedTokens(chainId: string): Token[] | undefined;
export { isEvmAddress, isSolanaAddress, isValidTokenAddress, isSolanaChain };
//# sourceMappingURL=tokenResolver.d.ts.map