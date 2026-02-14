/**
 * Policy Engine
 *
 * Enforces security policies for DeFi operations including:
 * - Spend limits per transaction and daily
 * - Allowed chain and token allowlists
 * - Blocked recipient addresses
 * - Maximum slippage tolerance
 * - Simulation requirements
 */
import { BridgeOperation, PolicyConfig } from '../types';
/**
 * Policy check result
 */
export interface PolicyCheckResult {
    allowed: boolean;
    reason?: string;
    details?: Record<string, unknown>;
}
/**
 * Policy Engine class for enforcing security constraints
 */
export declare class PolicyEngine {
    private config;
    constructor(policyId?: string);
    /**
     * Load policy configuration from environment
     *
     * @param policyId - Optional policy profile ID for custom limits
     * @returns The policy configuration
     */
    private loadPolicyConfig;
    /**
     * Check if a chain is allowed
     *
     * @param chainId - The chain ID to check
     * @returns Policy check result
     */
    private checkChainAllowed;
    /**
     * Check if a token is allowed on a specific chain
     *
     * @param chainId - The chain ID
     * @param token - The token address or symbol
     * @returns Policy check result
     */
    private checkTokenAllowed;
    /**
     * Check if a recipient is blocked
     *
     * @param recipient - The recipient address
     * @returns Policy check result
     */
    private checkRecipientNotBlocked;
    /**
     * Check bridge amount against limits
     *
     * @param token - The token address or symbol
     * @param amount - The amount in human-readable units
     * @returns Policy check result
     */
    private checkBridgeAmount;
    /**
     * Check a bridge operation against all policies
     *
     * @param operation - The bridge operation to validate
     * @returns Policy check result
     */
    checkBridge(operation: BridgeOperation): Promise<PolicyCheckResult>;
    /**
     * Get the current policy configuration
     * @returns The policy configuration
     */
    getConfig(): PolicyConfig;
    /**
     * Get available policy IDs from the configuration
     * @returns Array of available policy IDs
     */
    getAvailablePolicies(): string[];
    /**
     * Check swap input amount against USD limits
     */
    private checkSwapAmount;
    /**
     * Check slippage against maximum allowed
     */
    private checkSlippage;
    /**
     * Check a swap operation against all policies
     */
    checkSwap(params: {
        walletId: string;
        srcChainId: string;
        dstChainId: string;
        srcToken: string;
        dstToken: string;
        inputAmount: string;
        slippageBps: number;
        policyId?: string;
    }): Promise<PolicyCheckResult>;
    /**
     * Check borrow amount against limits
     */
    private checkBorrowAmount;
    /**
     * Check a money market operation against all policies
     */
    checkMoneyMarket(params: {
        walletId: string;
        chainId: string;
        dstChainId?: string;
        token: string;
        amount: string;
        amountUsd?: number;
        operation: 'supply' | 'withdraw' | 'borrow' | 'repay';
        policyId?: string;
    }): Promise<PolicyCheckResult>;
}
//# sourceMappingURL=policyEngine.d.ts.map