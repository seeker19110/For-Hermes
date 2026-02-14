/**
 * Amped DeFi Plugin
 *
 * OpenClaw plugin for DeFi operations (swaps, bridging, money market)
 * via the SODAX SDK.
 */
import { TSchema } from '@sinclair/typebox';
/**
 * OpenClaw Plugin API (defined locally to avoid SDK dependency)
 */
interface OpenClawPluginApi {
    pluginConfig: Record<string, unknown>;
    logger: {
        info: (msg: string) => void;
        warn: (msg: string) => void;
        error: (msg: string) => void;
        debug: (msg: string) => void;
    };
    registerTool: (tool: {
        name: string;
        description: string;
        parameters: TSchema;
        execute: (toolCallId: string, params: unknown) => Promise<{
            content: Array<{
                type: 'text';
                text: string;
            }>;
            details?: unknown;
        }>;
    }) => void;
    registerService: (service: {
        id: string;
        start: () => void;
        stop: () => Promise<void> | void;
    }) => void;
    on: (event: string, handler: (event: unknown, ctx: unknown) => unknown) => void;
}
/**
 * OpenClaw Plugin Definition
 */
declare const _default: {
    id: string;
    name: string;
    description: string;
    kind: "tools";
    configSchema: import("@sinclair/typebox").TObject<{
        walletsJson: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
        rpcUrlsJson: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
        mode: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"execute">, import("@sinclair/typebox").TLiteral<"simulate">]>>;
        dynamicConfig: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
    }>;
    register(api: OpenClawPluginApi): void;
};
export default _default;
export * from './types';
export { getSodaxClient, getSodaxClientAsync, resetSodaxClient } from './sodax/client';
export { getSpokeProvider, getCacheStats, clearProviderCache } from './providers/spokeProviderFactory';
export type { SpokeProvider } from './providers/spokeProviderFactory';
export { EvmSpokeProvider, SonicSpokeProvider } from '@sodax/sdk';
export { PolicyEngine } from './policy/policyEngine';
export { WalletRegistry, getWalletRegistry } from './wallet/walletRegistry';
export { WalletManager, getWalletManager, resetWalletManager } from './wallet/walletManager';
export type { IWalletBackend, WalletInfo, WalletBackendType } from './wallet/types';
export declare function activate(): Promise<void>;
export declare function deactivate(): Promise<void>;
//# sourceMappingURL=index.d.ts.map