/**
 * Price Service - Fetches USD prices from SODAX reserves
 *
 * Uses the money market reserve data to get accurate USD prices
 * for tokens supported by the protocol.
 *
 * @module utils/priceService
 */
export interface TokenPrice {
    symbol: string;
    priceUsd: number;
    underlyingAsset: string;
}
export interface PriceMap {
    /** Map of symbol (lowercase) to USD price */
    bySymbol: Map<string, number>;
    /** Map of address (lowercase) to USD price */
    byAddress: Map<string, number>;
    /** Last update timestamp */
    timestamp: number;
}
/**
 * Fetch token prices from SODAX money market reserves
 *
 * The reserves contain `priceInMarketReferenceCurrency` which represents
 * the price in 8 decimal USD (100000000 = $1.00)
 */
export declare function fetchTokenPrices(): Promise<PriceMap>;
/**
 * Get USD price for a token by symbol
 */
export declare function getTokenPriceBySymbol(symbol: string): Promise<number | null>;
/**
 * Get USD price for a token by address
 */
export declare function getTokenPriceByAddress(address: string): Promise<number | null>;
/**
 * Calculate USD value for a token amount
 */
export declare function calculateUsdValue(symbol: string, amount: string | number): Promise<number | null>;
/**
 * Clear the price cache (useful for testing)
 */
export declare function clearPriceCache(): void;
//# sourceMappingURL=priceService.d.ts.map