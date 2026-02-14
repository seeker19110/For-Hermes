// scripts/monitor.js
// Core logic to check for large transactions on a given wallet list using Public RPC.

const axios = require('axios');

// Public RPC Endpoint (Free, no key required)
const RPC_URL = 'https://eth.public-rpc.com';

// Target Wallets (Example: Binance Hot Wallet, Foundation, etc.)
const WALLET_ADDRESSES = [
    '0xBE0eB53F46cd790Cd13851d5EfF43D12404d33E8', // Binance 7 (Known huge wallet)
    '0xAb5801a7D398351b8bE11C439e05C5B3259aeC9B', // Vitalik Buterin (Vb 3)
];

const BALANCE_THRESHOLD_ETH = 100; // Reporting threshold

async function checkWhales() {
    console.log("🐳 Starting Whale Monitor (Public RPC)...");

    for (const address of WALLET_ADDRESSES) {
        try {
            // RPC Payload: eth_getBalance
            const payload = {
                jsonrpc: "2.0",
                method: "eth_getBalance",
                params: [address, "latest"],
                id: 1
            };

            const response = await axios.post(RPC_URL, payload);
            const hexBalance = response.data.result;
            
            if (hexBalance) {
                // Convert Hex to BigInt then to Number (ETH)
                const balanceWei = BigInt(hexBalance);
                const balanceEth = Number(balanceWei) / 10**18;

                console.log("Checking " + address + "...");
                console.log("Balance: " + balanceEth.toFixed(2) + " ETH");

                if (balanceEth > BALANCE_THRESHOLD_ETH) {
                    console.log("🚨 WHALE DETECTED: Wallet holds > " + BALANCE_THRESHOLD_ETH + " ETH");
                }
            } else {
                console.log("No data for " + address);
            }

        } catch (error) {
            console.error("Error checking wallet " + address + ":", error.message);
        }
    }
    console.log("✅ Monitor run complete.");
}

// Execute
checkWhales();