/**
 * SODAX API Client
 *
 * Provides access to SODAX backend API endpoints for querying intents,
 * user history, and other off-chain data.
 */
export interface SodaxApiConfig {
    baseUrl?: string;
    apiKey?: string;
    timeoutMs?: number;
}
export interface PaginationParams {
    offset?: number;
    limit?: number;
}
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    offset: number;
    limit: number;
}
export interface IntentState {
    exists: boolean;
    remainingInput: string;
    receivedOutput: string;
    pendingPayment: boolean;
}
export interface IntentEvent {
    eventType: string;
    txHash: string;
    logIndex: number;
    blockNumber: number;
    intentState: IntentState;
}
export interface IntentDetails {
    intentId: string;
    creator: string;
    inputToken: string;
    outputToken: string;
    inputAmount: string;
    minOutputAmount: string;
    deadline: string;
    allowPartialFill: boolean;
    srcChain: number;
    dstChain: number;
    srcAddress: string;
    dstAddress: string;
    solver: string;
    data: string;
}
export interface UserIntent {
    intentHash: string;
    txHash: string;
    logIndex: number;
    chainId: number;
    blockNumber: number;
    open: boolean;
    intent: IntentDetails;
    events: IntentEvent[];
    createdAt: string;
}
export interface UserIntentFilters {
    open?: boolean;
    srcChain?: number;
    dstChain?: number;
    inputToken?: string;
    outputToken?: string;
}
export declare class SodaxApiClient {
    private baseUrl;
    private apiKey?;
    private timeoutMs;
    constructor(config?: SodaxApiConfig);
    /**
     * Get intent by intentHash
     * Most reliable lookup method - works for all intents
     */
    getIntentByHash(intentHash: string): Promise<UserIntent | null>;
    /**
     * Get intent by transaction hash
     * NOTE: This expects the HUB chain (Sonic) transaction hash, NOT spoke chain tx
     */
    getIntentByTxHash(txHash: string): Promise<UserIntent | null>;
    getUserIntents(userAddress: string, pagination?: PaginationParams, filters?: UserIntentFilters): Promise<PaginatedResponse<UserIntent>>;
    getOpenIntents(userAddress: string, pagination?: PaginationParams): Promise<PaginatedResponse<UserIntent>>;
    getIntentHistory(userAddress: string, pagination?: PaginationParams): Promise<PaginatedResponse<UserIntent>>;
    private fetchWithTimeout;
    private isValidAddress;
}
export declare function getSodaxApiClient(config?: SodaxApiConfig): SodaxApiClient;
export declare function resetSodaxApiClient(): void;
//# sourceMappingURL=sodaxApi.d.ts.map