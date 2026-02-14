/**
 * SODAX SDK Client Singleton
 *
 * Provides a singleton instance of the SODAX SDK client with lazy initialization.
 * Uses dynamic configuration by default to fetch live token lists and routes.
 */
import { Sodax } from "@sodax/sdk";
/**
 * Get the singleton SODAX client instance
 * Initializes on first call if not already initialized
 */
export declare function getSodaxClientAsync(): Promise<Sodax>;
/**
 * Synchronous accessor for the SODAX client
 * Throws if the client hasn't been initialized yet
 */
export declare function getSodaxClient(): Sodax;
/**
 * Pre-initialize the SODAX client at plugin startup
 */
export declare function preInitializeSodax(): Promise<void>;
/**
 * Reset the SODAX client (useful for testing)
 */
export declare function resetSodaxClient(): void;
/**
 * SodaxClient class wrapper for backward compatibility
 */
export declare class SodaxClient {
    private static instance;
    static getClient(): Promise<Sodax>;
    static reset(): void;
}
//# sourceMappingURL=client.d.ts.map