/**
 * Discovery/Read Tools for Amped DeFi Plugin
 *
 * These tools provide read-only access to:
 * - Supported chains and tokens
 * - Wallet address resolution
 * - Money market positions and reserves
 *
 * @module tools/discovery
 */
import { Static } from '@sinclair/typebox';
/**
 * Schema for amped_supported_chains - no parameters required
 */
declare const SupportedChainsSchema: import("@sinclair/typebox").TObject<{}>;
/**
 * Schema for amped_supported_tokens
 */
declare const SupportedTokensSchema: import("@sinclair/typebox").TObject<{
    module: import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"swaps">, import("@sinclair/typebox").TLiteral<"bridge">, import("@sinclair/typebox").TLiteral<"moneyMarket">]>;
    chainId: import("@sinclair/typebox").TString;
}>;
/**
 * Schema for amped_wallet_address
 */
declare const WalletAddressSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
}>;
/**
 * Schema for amped_money_market_positions
 */
declare const MoneyMarketPositionsSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    chainId: import("@sinclair/typebox").TString;
}>;
/**
 * Schema for amped_money_market_reserves
 */
declare const MoneyMarketReservesSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
}>;
/**
 * Schema for amped_cross_chain_positions
 * Get aggregated positions view across all chains
 */
declare const CrossChainPositionsSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    chainIds: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TArray<import("@sinclair/typebox").TString>>;
    includeZeroBalances: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    minUsdValue: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
}>;
/**
 * Schema for amped_user_intents
 * Query user intent history from SODAX API
 */
declare const UserIntentsSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    status: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"all">, import("@sinclair/typebox").TLiteral<"open">, import("@sinclair/typebox").TLiteral<"closed">]>>;
    limit: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    offset: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
}>;
/**
 * Schema for amped_list_wallets - List all configured wallets
 */
declare const ListWalletsSchema: import("@sinclair/typebox").TObject<{}>;
type SupportedChainsParams = Static<typeof SupportedChainsSchema>;
type SupportedTokensParams = Static<typeof SupportedTokensSchema>;
type WalletAddressParams = Static<typeof WalletAddressSchema>;
type MoneyMarketPositionsParams = Static<typeof MoneyMarketPositionsSchema>;
type ListWalletsParams = Static<typeof ListWalletsSchema>;
type MoneyMarketReservesParams = Static<typeof MoneyMarketReservesSchema>;
type CrossChainPositionsParams = Static<typeof CrossChainPositionsSchema>;
type UserIntentsParams = Static<typeof UserIntentsSchema>;
/**
 * AgentTools interface for registering tools with the OpenClaw framework
 */
interface AgentTools {
    register(tool: {
        name: string;
        summary: string;
        description?: string;
        schema: unknown;
        handler: (params: unknown) => Promise<unknown>;
    }): void;
}
/**
 * Get supported spoke chains from SODAX configuration
 */
declare function handleSupportedChains(_params: SupportedChainsParams): Promise<unknown>;
/**
 * Get supported tokens for a specific module and chain
 */
declare function handleSupportedTokens(params: SupportedTokensParams): Promise<unknown>;
/**
 * Get wallet address by walletId
 * Returns enhanced wallet info with source and supported chains
 */
declare function handleWalletAddress(params: WalletAddressParams): Promise<unknown>;
/**
 * Get user money market positions (humanized format)
 */
declare function handleMoneyMarketPositions(params: MoneyMarketPositionsParams): Promise<unknown>;
/**
 * Get money market reserves (humanized format)
 * Hub-centric: returns reserves across all markets
 */
declare function handleMoneyMarketReserves(params: MoneyMarketReservesParams): Promise<unknown>;
/**
 * Get aggregated money market positions across all chains
 *
 * This provides a unified view of:
 * - Total supply/borrow across all networks
 * - Health factor and liquidation risk
 * - Available borrowing power
 * - Net position and APY
 * - Risk metrics and recommendations
 */
declare function handleCrossChainPositions(params: CrossChainPositionsParams): Promise<unknown>;
/**
 * Get user intents from SODAX API
 *
 * Queries the backend API for intent history including:
 * - Open/pending intents
 * - Filled intents
 * - Cancelled/expired intents
 * - Event history for each intent
 */
declare function handleUserIntents(params: UserIntentsParams): Promise<unknown>;
/**
 * List all configured wallets with their nicknames, types, and supported chains
 */
declare function handleListWallets(_params: ListWalletsParams): Promise<unknown>;
/**
 * Register all discovery tools with the agent tools registry
 *
 * @param agentTools - The OpenClaw AgentTools instance
 */
export declare function registerDiscoveryTools(agentTools: AgentTools): void;
export { SupportedChainsSchema, SupportedTokensSchema, WalletAddressSchema, MoneyMarketPositionsSchema, MoneyMarketReservesSchema, CrossChainPositionsSchema, UserIntentsSchema, ListWalletsSchema, };
export { handleSupportedChains, handleSupportedTokens, handleWalletAddress, handleMoneyMarketPositions, handleMoneyMarketReserves, handleCrossChainPositions, handleUserIntents, handleListWallets, };
//# sourceMappingURL=discovery.d.ts.map