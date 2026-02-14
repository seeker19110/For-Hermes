/**
 * Portfolio Summary Tool
 *
 * Provides a unified view of all wallet balances and positions.
 * Queries native tokens and major stablecoins via RPC, plus money market positions.
 *
 * @module tools/portfolio
 */
import { Static } from '@sinclair/typebox';
/**
 * Schema for amped_portfolio_summary
 */
export declare const PortfolioSummarySchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    chains: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TArray<import("@sinclair/typebox").TString>>;
    includeZeroBalances: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
type PortfolioSummaryParams = Static<typeof PortfolioSummarySchema>;
/**
 * Handle portfolio summary request
 */
export declare function handlePortfolioSummary(params: PortfolioSummaryParams): Promise<unknown>;
/**
 * Get all Solana balances for a wallet
 */
export declare function getSolanaWalletBalances(address: string, includeZeroBalances?: boolean): Promise<{
    chainId: string;
    chainName: string;
    native: {
        symbol: string;
        balance: string;
        usdValue?: string;
    };
    tokens: Array<{
        symbol: string;
        balance: string;
        address: string;
        usdValue?: string;
    }>;
    chainTotalUsd?: string;
} | null>;
export {};
//# sourceMappingURL=portfolio.d.ts.map