/**
 * Swap Tools for Amped DeFi Plugin
 *
 * Provides OpenClaw tools for cross-chain swap operations using SODAX SDK:
 * - amped_swap_quote: Get exact-in/exact-out quotes
 * - amped_swap_execute: Execute swaps with policy enforcement
 * - amped_swap_status: Poll intent status
 * - amped_swap_cancel: Cancel active intents
 */
import { Static } from '@sinclair/typebox';
import type { AgentTools } from '../types';
declare const SwapQuoteRequestSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    srcChainId: import("@sinclair/typebox").TString;
    dstChainId: import("@sinclair/typebox").TString;
    srcToken: import("@sinclair/typebox").TString;
    dstToken: import("@sinclair/typebox").TString;
    amount: import("@sinclair/typebox").TString;
    type: import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"exact_input">, import("@sinclair/typebox").TLiteral<"exact_output">]>;
    slippageBps: import("@sinclair/typebox").TNumber;
    recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
}>;
declare const SwapExecuteParamsSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    quote: import("@sinclair/typebox").TObject<{
        srcChainId: import("@sinclair/typebox").TString;
        dstChainId: import("@sinclair/typebox").TString;
        srcToken: import("@sinclair/typebox").TString;
        dstToken: import("@sinclair/typebox").TString;
        inputAmount: import("@sinclair/typebox").TString;
        outputAmount: import("@sinclair/typebox").TString;
        slippageBps: import("@sinclair/typebox").TNumber;
        deadline: import("@sinclair/typebox").TNumber;
        minOutputAmount: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
        maxInputAmount: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
        recipient: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    }>;
    maxSlippageBps: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
    policyId: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    skipSimulation: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    timeoutMs: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TNumber>;
}>;
declare const SwapStatusParamsSchema: import("@sinclair/typebox").TObject<{
    txHash: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    intentHash: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
}>;
declare const SwapCancelParamsSchema: import("@sinclair/typebox").TObject<{
    walletId: import("@sinclair/typebox").TString;
    intent: import("@sinclair/typebox").TObject<{
        id: import("@sinclair/typebox").TString;
        srcChainId: import("@sinclair/typebox").TString;
        dstChainId: import("@sinclair/typebox").TString;
        srcToken: import("@sinclair/typebox").TString;
        dstToken: import("@sinclair/typebox").TString;
        amount: import("@sinclair/typebox").TString;
        deadline: import("@sinclair/typebox").TNumber;
    }>;
    srcChainId: import("@sinclair/typebox").TString;
}>;
type SwapQuoteRequest = Static<typeof SwapQuoteRequestSchema>;
type SwapExecuteParams = Static<typeof SwapExecuteParamsSchema>;
type SwapStatusParams = Static<typeof SwapStatusParamsSchema>;
type SwapCancelParams = Static<typeof SwapCancelParamsSchema>;
declare function handleSwapQuote(params: SwapQuoteRequest): Promise<Record<string, unknown>>;
declare function handleSwapExecute(params: SwapExecuteParams): Promise<Record<string, unknown>>;
declare function handleSwapStatus(params: SwapStatusParams): Promise<Record<string, unknown>>;
declare function handleSwapCancel(params: SwapCancelParams): Promise<Record<string, unknown>>;
export declare function registerSwapTools(agentTools: AgentTools): void;
export { SwapQuoteRequestSchema as SwapQuoteSchema, SwapExecuteParamsSchema as SwapExecuteSchema, SwapStatusParamsSchema as SwapStatusSchema, SwapCancelParamsSchema as SwapCancelSchema, };
export { handleSwapQuote, handleSwapExecute, handleSwapStatus, handleSwapCancel, };
//# sourceMappingURL=swap.d.ts.map