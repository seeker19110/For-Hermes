/**
 * EVM Wallet Skill Backend
 *
 * Loads wallet from ~/.evm-wallet.json (created by evm-wallet-skill)
 */
import { existsSync, readFileSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';
import { SODAX_SUPPORTED_CHAINS } from '../types';
/**
 * Default path to evm-wallet-skill wallet file
 */
const DEFAULT_WALLET_PATH = join(homedir(), '.evm-wallet.json');
/**
 * Backend for evm-wallet-skill wallets
 * Supports all SODAX chains (local key signing)
 */
export class EvmWalletSkillBackend {
    type = 'evm-wallet-skill';
    nickname;
    supportedChains;
    walletPath;
    cachedWallet = null;
    constructor(options) {
        this.nickname = options.nickname;
        this.walletPath = options.path || DEFAULT_WALLET_PATH;
        this.supportedChains = options.chains || [...SODAX_SUPPORTED_CHAINS];
    }
    /**
     * Load wallet from file (cached)
     */
    loadWallet() {
        if (this.cachedWallet)
            return this.cachedWallet;
        if (!existsSync(this.walletPath)) {
            throw new Error(`Wallet file not found: ${this.walletPath}\n` +
                `Run: git clone https://github.com/amped-finance/evm-wallet-skill.git ~/.openclaw/skills/evm-wallet-skill\n` +
                `     cd ~/.openclaw/skills/evm-wallet-skill && npm install && node src/setup.js`);
        }
        try {
            const content = readFileSync(this.walletPath, 'utf-8');
            this.cachedWallet = JSON.parse(content);
            return this.cachedWallet;
        }
        catch (error) {
            throw new Error(`Failed to load wallet from ${this.walletPath}: ${error}`);
        }
    }
    async getAddress() {
        const wallet = this.loadWallet();
        return wallet.address;
    }
    supportsChain(chainId) {
        return this.supportedChains.includes(chainId);
    }
    async getPrivateKey() {
        const wallet = this.loadWallet();
        const key = wallet.privateKey;
        return key.startsWith('0x') ? key : `0x${key}`;
    }
    async isReady() {
        try {
            this.loadWallet();
            return true;
        }
        catch {
            return false;
        }
    }
}
/**
 * Create an evm-wallet-skill backend
 */
export function createEvmWalletSkillBackend(options = {}) {
    return new EvmWalletSkillBackend({
        nickname: options.nickname || 'main',
        path: options.path,
        chains: options.chains,
    });
}
//# sourceMappingURL=EvmWalletSkillBackend.js.map