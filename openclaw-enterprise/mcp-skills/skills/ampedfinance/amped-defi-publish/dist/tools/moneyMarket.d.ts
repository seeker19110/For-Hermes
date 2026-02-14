/**
 * Money Market Tools for Amped DeFi Plugin
 *
 * Provides advanced supply, withdraw, borrow, and repay operations for the SODAX money market.
 * Supports both same-chain and cross-chain operations (e.g., supply on Chain A, borrow to Chain B).
 *
 * Key capabilities:
 * - Supply: Deposit tokens as collateral on any supported chain
 * - Borrow: Borrow tokens to any chain (cross-chain capable)
 * - Withdraw: Withdraw supplied tokens from any chain
 * - Repay: Repay borrowed tokens from any chain
 * - Intent-based operations: Create intents for custom flows
 *
 * Cross-chain flows:
 * 1. Supply on Chain A → Borrow to Chain B (different destination)
 * 2. Supply on Chain A → Borrow on Chain A (same chain)
 * 3. Cross-chain repay: Repay debt from any chain
 * 4. Cross-chain withdraw: Withdraw collateral to any chain
 */
import { Static } from "@sinclair/typebox";
import { AgentTools } from "../types";
/**
 * Base schema for money market operations
 */
declare const MoneyMarketBaseSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    chainId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
/**
 * Supply operation schema
 * Supply tokens as collateral to the money market on the specified chain
 */
declare const MoneyMarketSupplySchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    dstChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    useAsCollateral: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
/**
 * Withdraw operation schema
 * Withdraw supplied tokens from the money market
 */
declare const MoneyMarketWithdrawSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    dstChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    withdrawType: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"default">, import("@sinclair/typebox").TLiteral<"collateral">, import("@sinclair/typebox").TLiteral<"all">]>>;
}>;
/**
 * Borrow operation schema
 * Borrow tokens from the money market
 *
 * Key feature: Can borrow to a DIFFERENT chain than where collateral is supplied!
 * Example: Supply USDC on Ethereum, borrow USDT to Arbitrum
 */
declare const MoneyMarketBorrowSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    dstChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    interestRateMode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<1>, import("@sinclair/typebox").TLiteral<2>]>>;
    referralCode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
}>;
/**
 * Repay operation schema
 * Repay borrowed tokens to the money market
 */
declare const MoneyMarketRepaySchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    interestRateMode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<1>, import("@sinclair/typebox").TLiteral<2>]>>;
    repayAll: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    collateralChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
}>;
/**
 * Create Intent schemas for advanced users
 * These allow building custom multi-step flows
 */
declare const CreateSupplyIntentSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    dstChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    useAsCollateral: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    raw: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
declare const CreateBorrowIntentSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    dstChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    interestRateMode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<1>, import("@sinclair/typebox").TLiteral<2>]>>;
    referralCode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    raw: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
declare const CreateWithdrawIntentSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    dstChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    withdrawType: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"default">, import("@sinclair/typebox").TLiteral<"collateral">, import("@sinclair/typebox").TLiteral<"all">]>>;
    raw: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
declare const CreateRepayIntentSchema: import("@sinclair/typebox").TObject<{
    chainId: import("@sinclair/typebox").TString;
    walletId: import("@sinclair/typebox").TString;
    token: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    interestRateMode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<1>, import("@sinclair/typebox").TLiteral<2>]>>;
    repayAll: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    collateralChainId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    raw: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
interface MoneyMarketOperationResult {
    success: boolean;
    txHash?: string;
    status: "success" | "pending" | "failed";
    spokeTxHash?: string;
    hubTxHash?: string;
    intentHash?: string;
    operation: string;
    chainId: string;
    dstChainId?: string;
    token: string;
    amount: string;
    message?: string;
    warnings?: string[];
    isCrossChain?: boolean;
    srcSpokeTxHash?: string;
    dstSpokeTxHash?: string;
    rawIntent?: unknown;
}
interface IntentResult extends MoneyMarketOperationResult {
    intentData: unknown;
    requiresSubmission: boolean;
}
/**
 * Supply tokens to the money market
 *
 * Supports cross-chain supply: supply tokens on chainId, collateral is recorded on dstChainId (if different)
 */
declare function handleSupply(params: Static<typeof MoneyMarketSupplySchema>): Promise<MoneyMarketOperationResult>;
/**
 * Withdraw tokens from the money market
 *
 * Supports cross-chain withdraw: withdraw collateral from chainId, receive tokens on dstChainId
 */
declare function handleWithdraw(params: Static<typeof MoneyMarketWithdrawSchema>): Promise<MoneyMarketOperationResult>;
/**
 * Borrow tokens from the money market
 *
 * KEY FEATURE: Can borrow to a DIFFERENT chain than where collateral is supplied!
 * Example: Supply USDC on Ethereum (chainId), borrow USDT to Arbitrum (dstChainId)
 *
 * This is a powerful cross-chain DeFi primitive that allows:
 * 1. Accessing liquidity without moving collateral
 * 2. Arbitraging interest rates across chains
 * 3. Efficient capital utilization across the entire SODAX network
 */
declare function handleBorrow(params: Static<typeof MoneyMarketBorrowSchema>): Promise<MoneyMarketOperationResult>;
/**
 * Repay borrowed tokens to the money market
 *
 * Supports cross-chain repay: repay debt using tokens from a different chain
 */
declare function handleRepay(params: Static<typeof MoneyMarketRepaySchema>): Promise<MoneyMarketOperationResult>;
/**
 * Create a supply intent without executing (for custom flows)
 */
declare function handleCreateSupplyIntent(params: Static<typeof CreateSupplyIntentSchema>): Promise<IntentResult>;
/**
 * Create a borrow intent without executing (for custom flows)
 */
declare function handleCreateBorrowIntent(params: Static<typeof CreateBorrowIntentSchema>): Promise<IntentResult>;
/**
 * Registers all money market tools with the agent tools registry
 */
export declare function registerMoneyMarketTools(agentTools: AgentTools): void;
export { MoneyMarketBaseSchema, MoneyMarketSupplySchema, MoneyMarketWithdrawSchema, MoneyMarketBorrowSchema, MoneyMarketRepaySchema, CreateSupplyIntentSchema, CreateWithdrawIntentSchema, CreateBorrowIntentSchema, CreateRepayIntentSchema, handleSupply, handleWithdraw, handleBorrow, handleRepay, handleCreateSupplyIntent, handleCreateBorrowIntent, };
export { MoneyMarketSupplySchema as MmSupplySchema, MoneyMarketWithdrawSchema as MmWithdrawSchema, MoneyMarketBorrowSchema as MmBorrowSchema, MoneyMarketRepaySchema as MmRepaySchema, handleSupply as handleMmSupply, handleWithdraw as handleMmWithdraw, handleBorrow as handleMmBorrow, handleRepay as handleMmRepay, };
export type { MoneyMarketOperationResult, IntentResult };
//# sourceMappingURL=moneyMarket.d.ts.map