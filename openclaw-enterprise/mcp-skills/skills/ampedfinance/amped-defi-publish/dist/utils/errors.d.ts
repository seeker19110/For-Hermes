/**
 * Error Handling Utilities
 *
 * Provides standardized error handling, error codes, and user-friendly error messages
 * for all Amped DeFi operations.
 */
/**
 * Standard error codes for Amped DeFi operations
 */
export declare enum ErrorCode {
    POLICY_SLIPPAGE_EXCEEDED = "POLICY_SLIPPAGE_EXCEEDED",
    POLICY_SPEND_LIMIT_EXCEEDED = "POLICY_SPEND_LIMIT_EXCEEDED",
    POLICY_CHAIN_NOT_ALLOWED = "POLICY_CHAIN_NOT_ALLOWED",
    POLICY_TOKEN_NOT_ALLOWED = "POLICY_TOKEN_NOT_ALLOWED",
    POLICY_RECIPIENT_BLOCKED = "POLICY_RECIPIENT_BLOCKED",
    WALLET_NOT_FOUND = "WALLET_NOT_FOUND",
    WALLET_INVALID_ADDRESS = "WALLET_INVALID_ADDRESS",
    WALLET_MISSING_PRIVATE_KEY = "WALLET_MISSING_PRIVATE_KEY",
    WALLET_RESOLUTION_FAILED = "WALLET_RESOLUTION_FAILED",
    CHAIN_NOT_SUPPORTED = "CHAIN_NOT_SUPPORTED",
    RPC_URL_NOT_CONFIGURED = "RPC_URL_NOT_CONFIGURED",
    PROVIDER_CREATION_FAILED = "PROVIDER_CREATION_FAILED",
    SONIC_PROVIDER_REQUIRED = "SONIC_PROVIDER_REQUIRED",
    INSUFFICIENT_BALANCE = "INSUFFICIENT_BALANCE",
    INSUFFICIENT_ALLOWANCE = "INSUFFICIENT_ALLOWANCE",
    TOKEN_NOT_SUPPORTED = "TOKEN_NOT_SUPPORTED",
    TOKEN_DECIMALS_NOT_FOUND = "TOKEN_DECIMALS_NOT_FOUND",
    QUOTE_EXPIRED = "QUOTE_EXPIRED",
    QUOTE_NOT_FOUND = "QUOTE_NOT_FOUND",
    BRIDGE_NOT_AVAILABLE = "BRIDGE_NOT_AVAILABLE",
    SWAP_EXECUTION_FAILED = "SWAP_EXECUTION_FAILED",
    BRIDGE_EXECUTION_FAILED = "BRIDGE_EXECUTION_FAILED",
    MM_HEALTH_FACTOR_LOW = "MM_HEALTH_FACTOR_LOW",
    MM_CROSS_CHAIN_NOT_SUPPORTED = "MM_CROSS_CHAIN_NOT_SUPPORTED",
    MM_INSUFFICIENT_COLLATERAL = "MM_INSUFFICIENT_COLLATERAL",
    MM_POSITION_NOT_FOUND = "MM_POSITION_NOT_FOUND",
    TRANSACTION_FAILED = "TRANSACTION_FAILED",
    TRANSACTION_TIMEOUT = "TRANSACTION_TIMEOUT",
    TRANSACTION_REJECTED = "TRANSACTION_REJECTED",
    TRANSACTION_SIMULATION_FAILED = "TRANSACTION_SIMULATION_FAILED",
    SDK_NOT_INITIALIZED = "SDK_NOT_INITIALIZED",
    SDK_INITIALIZATION_FAILED = "SDK_INITIALIZATION_FAILED",
    INVALID_CONFIGURATION = "INVALID_CONFIGURATION",
    CONFIG_PARSE_ERROR = "CONFIG_PARSE_ERROR",
    UNKNOWN_ERROR = "UNKNOWN_ERROR",
    OPERATION_CANCELLED = "OPERATION_CANCELLED"
}
/**
 * Error severity levels
 */
export declare enum ErrorSeverity {
    INFO = "info",
    WARNING = "warning",
    ERROR = "error",
    CRITICAL = "critical"
}
/**
 * Structured error information
 */
export interface AmpedError {
    code: ErrorCode;
    message: string;
    severity: ErrorSeverity;
    remediation?: string;
    details?: Record<string, unknown>;
    cause?: Error;
}
/**
 * Error context for logging
 */
export interface ErrorContext {
    operation?: string;
    walletId?: string;
    chainId?: string;
    chainIds?: string[];
    token?: string;
    tokens?: string[];
    amount?: string;
    requestId?: string;
    txHash?: string;
    [key: string]: unknown;
}
/**
 * Amped DeFi Error class
 */
export declare class AmpedDefiError extends Error {
    readonly code: ErrorCode;
    readonly severity: ErrorSeverity;
    readonly remediation?: string;
    readonly details?: Record<string, unknown>;
    readonly context?: ErrorContext;
    constructor(code: ErrorCode, message: string, options?: {
        severity?: ErrorSeverity;
        remediation?: string;
        details?: Record<string, unknown>;
        context?: ErrorContext;
        cause?: Error;
    });
    /**
     * Convert to JSON-serializable object
     */
    toJSON(): AmpedError;
    /**
     * Get user-friendly error message
     */
    toUserMessage(): string;
}
/**
 * Create a policy error
 */
export declare function createPolicyError(code: ErrorCode, message: string, details?: {
    current?: unknown;
    limit?: unknown;
    [key: string]: unknown;
}, context?: ErrorContext): AmpedDefiError;
/**
 * Create a wallet error
 */
export declare function createWalletError(code: ErrorCode, walletId: string, cause?: Error, context?: ErrorContext): AmpedDefiError;
/**
 * Create a transaction error
 */
export declare function createTransactionError(code: ErrorCode, message: string, txHash?: string, cause?: Error, context?: ErrorContext): AmpedDefiError;
/**
 * Create an SDK error
 */
export declare function createSDKError(code: ErrorCode, message: string, cause?: Error, context?: ErrorContext): AmpedDefiError;
/**
 * Wrap an unknown error into an AmpedDefiError
 */
export declare function wrapError(error: unknown, fallbackCode?: ErrorCode, context?: ErrorContext): AmpedDefiError;
/**
 * Log an error with structured context
 */
export declare function logError(error: AmpedDefiError | Error, context?: ErrorContext): void;
/**
 * Check if an error is retryable
 */
export declare function isRetryableError(error: AmpedDefiError | Error): boolean;
/**
 * Get retry delay in milliseconds with exponential backoff
 */
export declare function getRetryDelay(attempt: number, baseDelay?: number): number;
//# sourceMappingURL=errors.d.ts.map