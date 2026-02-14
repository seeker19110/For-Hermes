/**
 * Environment Variable Backend
 *
 * Loads wallet from environment variables:
 * - AMPED_OC_WALLETS_JSON: JSON with wallet configs
 * - Or individual env vars for address/privateKey
 */
import { SODAX_SUPPORTED_CHAINS } from '../types';
/**
 * Environment variable wallet backend
 * Supports all SODAX chains (local key signing)
 */
export class EnvBackend {
    type = 'env';
    nickname;
    supportedChains;
    address = null;
    privateKey = null;
    envVar = null;
    constructor(config) {
        this.nickname = config.nickname;
        this.supportedChains = config.chains || [...SODAX_SUPPORTED_CHAINS];
        if (config.address && config.privateKey) {
            // Direct address/key provided
            this.address = config.address;
            this.privateKey = config.privateKey;
        }
        else if (config.envVar) {
            // Will load from env var
            this.envVar = config.envVar;
        }
    }
    /**
     * Load wallet from environment variable if needed
     */
    loadFromEnv() {
        if (this.address && this.privateKey) {
            return { address: this.address, privateKey: this.privateKey };
        }
        if (this.envVar) {
            const envValue = process.env[this.envVar];
            if (!envValue) {
                throw new Error(`Environment variable ${this.envVar} not set`);
            }
            try {
                const data = JSON.parse(envValue);
                this.address = data.address;
                this.privateKey = (data.privateKey.startsWith('0x')
                    ? data.privateKey
                    : `0x${data.privateKey}`);
                return { address: this.address, privateKey: this.privateKey };
            }
            catch (error) {
                throw new Error(`Failed to parse ${this.envVar}: ${error}`);
            }
        }
        throw new Error(`No wallet configuration for "${this.nickname}"`);
    }
    async getAddress() {
        const { address } = this.loadFromEnv();
        return address;
    }
    supportsChain(chainId) {
        return this.supportedChains.includes(chainId);
    }
    async getPrivateKey() {
        const { privateKey } = this.loadFromEnv();
        return privateKey;
    }
    async isReady() {
        try {
            this.loadFromEnv();
            return true;
        }
        catch {
            return false;
        }
    }
}
/**
 * Create env backend from direct config
 */
export function createEnvBackend(config) {
    return new EnvBackend(config);
}
/**
 * Load wallets from AMPED_OC_WALLETS_JSON environment variable
 * Returns multiple backends keyed by wallet name
 */
export function loadWalletsFromEnv() {
    const wallets = new Map();
    const walletsJson = process.env.AMPED_OC_WALLETS_JSON;
    if (!walletsJson)
        return wallets;
    try {
        const parsed = JSON.parse(walletsJson);
        for (const [name, wallet] of Object.entries(parsed)) {
            const backend = new EnvBackend({
                nickname: name,
                address: wallet.address,
                privateKey: (wallet.privateKey.startsWith('0x')
                    ? wallet.privateKey
                    : `0x${wallet.privateKey}`),
            });
            wallets.set(name.toLowerCase(), backend);
        }
        console.log(`[EnvBackend] Loaded ${wallets.size} wallet(s) from AMPED_OC_WALLETS_JSON`);
    }
    catch (error) {
        console.warn(`[EnvBackend] Failed to parse AMPED_OC_WALLETS_JSON: ${error}`);
    }
    return wallets;
}
//# sourceMappingURL=EnvBackend.js.map