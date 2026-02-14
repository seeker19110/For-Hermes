/**
 * SODAX SDK Client Singleton
 *
 * Provides a singleton instance of the SODAX SDK client with lazy initialization.
 * Uses dynamic configuration by default to fetch live token lists and routes.
 */
import { Sodax } from "@sodax/sdk";
// Singleton instance
let sodaxClient = null;
/**
 * HARDCODED PARTNER CONFIGURATION
 * These values are baked in and cannot be overridden.
 *
 * Fee is 0.2% (20 basis points)
 * SDK expects: percentage in bps where 100 = 1%, so 20 = 0.2%
 */
const PARTNER_FEE = {
    address: "0xd99C871c8130B03C8BB597A74fb5EAA7a46864Bb",
    percentage: 20, // 20 bps = 0.2%
};
/**
 * Initialize the SODAX SDK client
 * Always uses dynamic config to fetch live token lists and routes
 */
async function initializeSodax() {
    // Initialize SODAX with hardcoded partner fee on ALL services
    const sodax = new Sodax({
        swaps: { partnerFee: PARTNER_FEE },
        moneyMarket: { partnerFee: PARTNER_FEE },
        bridge: { partnerFee: PARTNER_FEE },
    });
    // Suppress SDK console output during initialization
    const originalWarn = console.warn;
    const originalLog = console.log;
    console.warn = () => { };
    console.log = () => { };
    try {
        // Initialize with dynamic config
        await sodax.initialize();
    }
    finally {
        // Restore console
        console.warn = originalWarn;
        console.log = originalLog;
    }
    return sodax;
}
/**
 * Get the singleton SODAX client instance
 * Initializes on first call if not already initialized
 */
export async function getSodaxClientAsync() {
    if (!sodaxClient) {
        sodaxClient = await initializeSodax();
    }
    return sodaxClient;
}
/**
 * Synchronous accessor for the SODAX client
 * Throws if the client hasn't been initialized yet
 */
export function getSodaxClient() {
    if (!sodaxClient) {
        throw new Error("SODAX client not initialized. Call getSodaxClientAsync() first.");
    }
    return sodaxClient;
}
/**
 * Pre-initialize the SODAX client at plugin startup
 */
export async function preInitializeSodax() {
    if (!sodaxClient) {
        sodaxClient = await initializeSodax();
    }
}
/**
 * Reset the SODAX client (useful for testing)
 */
export function resetSodaxClient() {
    sodaxClient = null;
}
/**
 * SodaxClient class wrapper for backward compatibility
 */
export class SodaxClient {
    static instance = null;
    static async getClient() {
        if (!SodaxClient.instance) {
            SodaxClient.instance = await initializeSodax();
            sodaxClient = SodaxClient.instance;
        }
        return SodaxClient.instance;
    }
    static reset() {
        SodaxClient.instance = null;
        sodaxClient = null;
    }
}
//# sourceMappingURL=client.js.map