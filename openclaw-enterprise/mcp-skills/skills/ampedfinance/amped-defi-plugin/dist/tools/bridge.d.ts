/**
 * Bridge Tools for Amped DeFi Plugin
 *
 * NOTE: Bridge operations use the swap infrastructure internally.
 * Cross-chain swaps and bridges are functionally equivalent in SODAX -
 * both use the intent-based cross-chain messaging system.
 *
 * Tools:
 * - amped_bridge_discover: Get bridgeable tokens for a route
 * - amped_bridge_quote: Check bridgeability and max amounts
 * - amped_bridge_execute: Execute bridge (delegates to swap)
 *
 * @module tools/bridge
 */
import { Static } from '@sinclair/typebox';
import { AgentTools } from '../types';
/**
 * Schema for amped_bridge_discover tool
 * Discover bridgeable tokens for a given source chain, destination chain, and source token
 */
declare const BridgeDiscoverSchema: import("@sinclair/typebox").TObject<{
    srcChainId: import("@sinclair/typebox").TString;
    dstChainId: import("@sinclair/typebox").TString;
    srcToken: import("@sinclair/typebox").TString;
}>;
/**
 * Schema for amped_bridge_quote tool
 * Check if a bridge route is valid and get maximum bridgeable amount
 */
declare const BridgeQuoteSchema: import("@sinclair/typebox").TObject<{
    srcChainId: import("@sinclair/typebox").TString;
    dstChainId: import("@sinclair/typebox").TString;
    srcToken: import("@sinclair/typebox").TString;
    dstToken: import("@sinclair/typebox").TString;
}>;
/**
 * Schema for amped_bridge_execute tool
 * Execute a bridge operation with full allowance check and approval flow
 */
declare const BridgeExecuteSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    srcChainId: import("@sinclair/typebox").TString;
    dstChainId: import("@sinclair/typebox").TString;
    srcToken: import("@sinclair/typebox").TString;
    dstToken: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
}>;
type BridgeDiscoverParams = Static<typeof BridgeDiscoverSchema>;
type BridgeQuoteParams = Static<typeof BridgeQuoteSchema>;
type BridgeExecuteParams = Static<typeof BridgeExecuteSchema>;
/**
 * Transaction result type for bridge execute
 */
interface TransactionResult {
    spokeTxHash: string;
    hubTxHash?: string;
}
/**
 * Handler for amped_bridge_discover
 * Retrieves tokens that can be bridged from the source chain to destination chain
 *
 * @param params - Discovery parameters (srcChainId, dstChainId, srcToken)
 * @returns List of bridgeable tokens
 */
declare function handleBridgeDiscover(params: BridgeDiscoverParams): Promise<{
    bridgeableTokens: string[];
}>;
/**
 * Handler for amped_bridge_quote
 * Checks if a bridge route is valid and returns the maximum bridgeable amount
 *
 * @param params - Quote parameters (srcChainId, dstChainId, srcToken, dstToken)
 * @returns Bridgeability status and maximum amount
 */
declare function handleBridgeQuote(params: BridgeQuoteParams): Promise<{
    isBridgeable: boolean;
    maxBridgeableAmount: string;
}>;
/**
 * Handler for amped_bridge_execute
 *
 * NOTE: Bridge operations are implemented via swap infrastructure.
 * Cross-chain swaps and bridges are functionally equivalent in SODAX -
 * both use the intent-based cross-chain messaging system.
 *
 * Flow:
 *   1. Get swap quote for the bridge route
 *   2. Execute swap (handles allowance, approval, and execution)
 *
 * @param params - Execution parameters
 * @returns Transaction result with status and tracking links
 */
declare function handleBridgeExecute(params: BridgeExecuteParams): Promise<TransactionResult>;
/**
 * Register all bridge tools with the agent tools registry
 *
 * @param agentTools - The agent tools registry
 */
export declare function registerBridgeTools(agentTools: AgentTools): void;
export { BridgeDiscoverSchema, BridgeQuoteSchema, BridgeExecuteSchema };
export { handleBridgeDiscover, handleBridgeQuote, handleBridgeExecute };
//# sourceMappingURL=bridge.d.ts.map