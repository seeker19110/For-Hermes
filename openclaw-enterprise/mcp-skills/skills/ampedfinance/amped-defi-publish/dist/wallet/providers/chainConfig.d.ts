/**
 * Chain Configuration for Amped Wallet Provider
 *
 * Complete chain configuration for all SODAX-supported EVM chains.
 *
 * Note: We maintain our own chain definitions to avoid viem version
 * mismatches with @sodax/wallet-sdk-core. The SDK's getEvmViemChain()
 * is used as a fallback for future chain additions.
 */
import { type Chain } from 'viem';
/**
 * Chain ID constants matching @sodax/types
 */
export declare const CHAIN_IDS: {
    readonly ETHEREUM: 1;
    readonly ARBITRUM: 42161;
    readonly OPTIMISM: 10;
    readonly BASE: 8453;
    readonly POLYGON: 137;
    readonly BSC: 56;
    readonly AVALANCHE: 43114;
    readonly SONIC: 146;
    readonly LIGHTLINK: 1890;
    readonly HYPEREVM: 999;
    readonly KAIA: 8217;
};
/**
 * SDK chain ID format mapping (e.g., 'ethereum', '0x2105.base')
 */
export declare const SDK_CHAIN_ID_MAP: Record<string, number>;
/**
 * HyperEVM chain definition
 * Matches @sodax/wallet-sdk-core hyper definition
 */
export declare const hyper: {
    blockExplorers: {
        readonly default: {
            readonly name: "HyperEVMScan";
            readonly url: "https://hyperevmscan.io/";
        };
    };
    blockTime?: number | undefined;
    contracts: {
        readonly multicall3: {
            readonly address: "0xcA11bde05977b3631167028862bE2a173976CA11";
            readonly blockCreated: 13051;
        };
    };
    ensTlds?: readonly string[] | undefined;
    id: 999;
    name: "HyperEVM";
    nativeCurrency: {
        readonly decimals: 18;
        readonly name: "HYPE";
        readonly symbol: "HYPE";
    };
    experimental_preconfirmationTime?: number | undefined;
    rpcUrls: {
        readonly default: {
            readonly http: readonly ["https://rpc.hyperliquid.xyz/evm"];
        };
    };
    sourceId?: number | undefined;
    testnet?: boolean | undefined;
    custom?: Record<string, unknown>;
    extendSchema?: Record<string, unknown>;
    fees?: import("viem").ChainFees<undefined>;
    formatters?: undefined;
    prepareTransactionRequest?: ((args: import("viem").PrepareTransactionRequestParameters, options: {
        phase: "beforeFillTransaction" | "beforeFillParameters" | "afterFillParameters";
    }) => Promise<import("viem").PrepareTransactionRequestParameters>) | [fn: ((args: import("viem").PrepareTransactionRequestParameters, options: {
        phase: "beforeFillTransaction" | "beforeFillParameters" | "afterFillParameters";
    }) => Promise<import("viem").PrepareTransactionRequestParameters>) | undefined, options: {
        runAt: readonly ("beforeFillTransaction" | "beforeFillParameters" | "afterFillParameters")[];
    }] | undefined;
    serializers?: import("viem").ChainSerializers<undefined, import("viem").TransactionSerializable>;
    verifyHash?: ((client: import("viem").Client, parameters: import("viem").VerifyHashActionParameters) => Promise<import("viem").VerifyHashActionReturnType>) | undefined;
    extend: <const extended_1 extends Record<string, unknown>>(extended: extended_1) => import("viem").Assign<import("viem").Assign<Chain<undefined>, {
        readonly id: 999;
        readonly name: "HyperEVM";
        readonly nativeCurrency: {
            readonly decimals: 18;
            readonly name: "HYPE";
            readonly symbol: "HYPE";
        };
        readonly rpcUrls: {
            readonly default: {
                readonly http: readonly ["https://rpc.hyperliquid.xyz/evm"];
            };
        };
        readonly blockExplorers: {
            readonly default: {
                readonly name: "HyperEVMScan";
                readonly url: "https://hyperevmscan.io/";
            };
        };
        readonly contracts: {
            readonly multicall3: {
                readonly address: "0xcA11bde05977b3631167028862bE2a173976CA11";
                readonly blockCreated: 13051;
            };
        };
    }>, extended_1>;
};
/**
 * Kaia chain definition
 */
export declare const kaia: {
    blockExplorers: {
        readonly default: {
            readonly name: "KaiaScan";
            readonly url: "https://kaiascan.io/";
        };
    };
    blockTime?: number | undefined;
    contracts?: import("viem").Prettify<{
        [key: string]: import("viem").ChainContract | {
            [sourceId: number]: import("viem").ChainContract | undefined;
        } | undefined;
    } & {
        ensRegistry?: import("viem").ChainContract | undefined;
        ensUniversalResolver?: import("viem").ChainContract | undefined;
        multicall3?: import("viem").ChainContract | undefined;
        erc6492Verifier?: import("viem").ChainContract | undefined;
    }> | undefined;
    ensTlds?: readonly string[] | undefined;
    id: 8217;
    name: "Kaia";
    nativeCurrency: {
        readonly decimals: 18;
        readonly name: "KAIA";
        readonly symbol: "KAIA";
    };
    experimental_preconfirmationTime?: number | undefined;
    rpcUrls: {
        readonly default: {
            readonly http: readonly ["https://public-en.node.kaia.io"];
        };
    };
    sourceId?: number | undefined;
    testnet?: boolean | undefined;
    custom?: Record<string, unknown>;
    extendSchema?: Record<string, unknown>;
    fees?: import("viem").ChainFees<undefined>;
    formatters?: undefined;
    prepareTransactionRequest?: ((args: import("viem").PrepareTransactionRequestParameters, options: {
        phase: "beforeFillTransaction" | "beforeFillParameters" | "afterFillParameters";
    }) => Promise<import("viem").PrepareTransactionRequestParameters>) | [fn: ((args: import("viem").PrepareTransactionRequestParameters, options: {
        phase: "beforeFillTransaction" | "beforeFillParameters" | "afterFillParameters";
    }) => Promise<import("viem").PrepareTransactionRequestParameters>) | undefined, options: {
        runAt: readonly ("beforeFillTransaction" | "beforeFillParameters" | "afterFillParameters")[];
    }] | undefined;
    serializers?: import("viem").ChainSerializers<undefined, import("viem").TransactionSerializable>;
    verifyHash?: ((client: import("viem").Client, parameters: import("viem").VerifyHashActionParameters) => Promise<import("viem").VerifyHashActionReturnType>) | undefined;
    extend: <const extended_1 extends Record<string, unknown>>(extended: extended_1) => import("viem").Assign<import("viem").Assign<Chain<undefined>, {
        readonly id: 8217;
        readonly name: "Kaia";
        readonly nativeCurrency: {
            readonly decimals: 18;
            readonly name: "KAIA";
            readonly symbol: "KAIA";
        };
        readonly rpcUrls: {
            readonly default: {
                readonly http: readonly ["https://public-en.node.kaia.io"];
            };
        };
        readonly blockExplorers: {
            readonly default: {
                readonly name: "KaiaScan";
                readonly url: "https://kaiascan.io/";
            };
        };
    }>, extended_1>;
};
/**
 * Default RPC URLs for all supported chains
 */
/**
 * FALLBACK RPC URLs for all supported chains
 * Primary RPCs should come from evm-wallet-skill (chains.js)
 * @see https://github.com/amped-finance/evm-wallet-skill
 */
export declare const DEFAULT_RPC_URLS: Record<number, string>;
/**
 * Resolve SDK chain ID format to numeric chain ID
 */
export declare function resolveChainId(sdkChainId: string | number): number;
/**
 * Get viem Chain configuration for a chain ID
 */
export declare function getViemChain(chainId: string | number): Chain;
/**
 * Get default RPC URL for a chain
 */
export declare function getDefaultRpcUrl(chainId: string | number): string;
/**
 * Check if a chain is supported
 */
export declare function isChainSupported(chainId: string | number): boolean;
/**
 * Get all supported chain IDs
 */
export declare function getSupportedChainIds(): number[];
/**
 * Get chain name
 */
export declare function getChainName(chainId: string | number): string;
//# sourceMappingURL=chainConfig.d.ts.map