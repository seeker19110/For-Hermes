/**
 * Wallet Management Tools
 *
 * Agent-driven wallet configuration:
 * - Add wallets with nicknames
 * - Rename existing wallets
 * - Remove wallets
 * - Set default wallet
 *
 * Changes persist to: ~/.openclaw/extensions/amped-defi/wallets.json
 */
import { Static } from '@sinclair/typebox';
/**
 * Schema for amped_add_wallet
 */
declare const AddWalletSchema: import("@sinclair/typebox").TObject<{
    nickname: import("@sinclair/typebox").TString;
    source: import("@sinclair/typebox").TUnion<[import("@sinclair/typebox").TLiteral<"evm-wallet-skill">, import("@sinclair/typebox").TLiteral<"bankr">, import("@sinclair/typebox").TLiteral<"env">]>;
    path: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    apiKey: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    apiUrl: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    address: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    privateKey: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TString>;
    chains: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TArray<import("@sinclair/typebox").TString>>;
}>;
/**
 * Schema for amped_rename_wallet
 */
declare const RenameWalletSchema: import("@sinclair/typebox").TObject<{
    currentNickname: import("@sinclair/typebox").TString;
    newNickname: import("@sinclair/typebox").TString;
}>;
/**
 * Schema for amped_remove_wallet
 */
declare const RemoveWalletSchema: import("@sinclair/typebox").TObject<{
    nickname: import("@sinclair/typebox").TString;
    confirm: import("@sinclair/typebox").TOptional<import("@sinclair/typebox").TBoolean>;
}>;
/**
 * Schema for amped_set_default_wallet
 */
declare const SetDefaultWalletSchema: import("@sinclair/typebox").TObject<{
    nickname: import("@sinclair/typebox").TString;
}>;
type AddWalletParams = Static<typeof AddWalletSchema>;
type RenameWalletParams = Static<typeof RenameWalletSchema>;
type RemoveWalletParams = Static<typeof RemoveWalletSchema>;
type SetDefaultWalletParams = Static<typeof SetDefaultWalletSchema>;
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
 * Add a new wallet with a nickname
 */
declare function handleAddWallet(params: AddWalletParams): Promise<unknown>;
/**
 * Rename a wallet
 */
declare function handleRenameWallet(params: RenameWalletParams): Promise<unknown>;
/**
 * Remove a wallet
 */
declare function handleRemoveWallet(params: RemoveWalletParams): Promise<unknown>;
/**
 * Set default wallet
 */
declare function handleSetDefaultWallet(params: SetDefaultWalletParams): Promise<unknown>;
/**
 * Register wallet management tools
 */
export declare function registerWalletManagementTools(agentTools: AgentTools): void;
export { AddWalletSchema, RenameWalletSchema, RemoveWalletSchema, SetDefaultWalletSchema, handleAddWallet, handleRenameWallet, handleRemoveWallet, handleSetDefaultWallet, };
//# sourceMappingURL=walletManagement.d.ts.map