/**
 * Cross-Chain Money Market Position Aggregator
 *
 * Aggregates user positions across all supported chains to provide a unified view
 * of their money market portfolio, including:
 * - Total supplied/borrowed across all chains
 * - Health factor and liquidation risk
 * - Available borrowing power
 * - Net position (supply - borrow)
 * - Cross-chain collateral utilization
 */
/**
 * Position data for a single token on a single chain
 */
export interface TokenPosition {
    chainId: string;
    token: {
        address: string;
        symbol: string;
        name: string;
        decimals: number;
        logoURI?: string;
    };
    supply: {
        balance: string;
        balanceUsd: string;
        balanceRaw: string;
        apy: number;
        isCollateral: boolean;
    };
    borrow: {
        balance: string;
        balanceUsd: string;
        balanceRaw: string;
        apy: number;
    };
    loanToValue: number;
    liquidationThreshold: number;
}
/**
 * Aggregated position summary across all chains
 */
export interface AggregatedPositionSummary {
    totalSupplyUsd: number;
    totalBorrowUsd: number;
    netWorthUsd: number;
    availableBorrowUsd: number;
    healthFactor: number | null;
    liquidationRisk: 'none' | 'low' | 'medium' | 'high';
    weightedSupplyApy: number;
    weightedBorrowApy: number;
    netApy: number;
}
/**
 * Chain-specific position summary
 */
export interface ChainPositionSummary {
    chainId: string;
    supplyUsd: number;
    borrowUsd: number;
    netWorthUsd: number;
    healthFactor: number | null;
    positionCount: number;
}
/**
 * Complete cross-chain position view
 */
export interface CrossChainPositionView {
    walletId: string;
    address: string;
    timestamp: string;
    summary: AggregatedPositionSummary;
    chainSummaries: ChainPositionSummary[];
    positions: TokenPosition[];
    collateralUtilization: {
        totalCollateralUsd: number;
        usedCollateralUsd: number;
        availableCollateralUsd: number;
        utilizationRate: number;
    };
    riskMetrics: {
        maxLtv: number;
        currentLtv: number;
        bufferUntilLiquidation: number;
        safeMaxBorrowUsd: number;
    };
}
/**
 * Options for position aggregation
 */
export interface AggregationOptions {
    /** Specific chains to query (defaults to all supported chains) */
    chainIds?: string[];
    /** Include zero-balance positions */
    includeZeroBalances?: boolean;
    /** Minimum USD value to include (positions below this are filtered out unless includeZeroBalances is true) */
    minUsdValue?: number;
}
/**
 * Aggregate money market positions across all supported chains
 *
 * @param walletId - The wallet identifier
 * @param options - Aggregation options
 * @returns Complete cross-chain position view
 */
export declare function aggregateCrossChainPositions(walletId: string, options?: AggregationOptions): Promise<CrossChainPositionView>;
/**
 * Format health factor for display
 */
export declare function formatHealthFactor(hf: number | null): string;
/**
 * Get health factor color/styling indicator
 */
export declare function getHealthFactorStatus(hf: number | null): {
    status: 'healthy' | 'caution' | 'danger' | 'critical';
    color: 'green' | 'yellow' | 'orange' | 'red';
};
/**
 * Get recommendation based on position health
 */
export declare function getPositionRecommendation(view: CrossChainPositionView): string[];
//# sourceMappingURL=positionAggregator.d.ts.map