#!/bin/bash
# Apiosk Wallet Setup - One-time configuration

set -e

WALLET_DIR="$HOME/.apiosk"
WALLET_FILE="$WALLET_DIR/wallet.json"
CONFIG_FILE="$WALLET_DIR/config.json"
SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🦞 Apiosk Wallet Setup"
echo ""

# Create directory
mkdir -p "$WALLET_DIR"

# Check if wallet exists
if [ -f "$WALLET_FILE" ] && [ "$1" != "--regenerate" ]; then
  echo "❌ Wallet already exists at $WALLET_FILE"
  echo "Use --regenerate to create a new wallet (WARNING: old wallet will be lost!)"
  exit 1
fi

# Install ethers if needed
if [ ! -d "$SKILL_DIR/node_modules/ethers" ]; then
  echo "Installing dependencies..."
  (cd "$SKILL_DIR" && npm install --production --quiet 2>/dev/null)
fi

echo "Generating new wallet..."

# Generate a proper Ethereum keypair using ethers.js
WALLET_JSON=$(node -e "
const { ethers } = require('$SKILL_DIR/node_modules/ethers');
const wallet = ethers.Wallet.createRandom();
console.log(JSON.stringify({
  address: wallet.address,
  private_key: wallet.privateKey,
  created_at: new Date().toISOString()
}));
")

ADDRESS=$(echo "$WALLET_JSON" | node -e "process.stdout.write(JSON.parse(require('fs').readFileSync('/dev/stdin','utf8')).address)")

# Save wallet (private key stored locally for on-chain transactions)
echo "$WALLET_JSON" > "$WALLET_FILE"
chmod 600 "$WALLET_FILE"

# Create config
cat > "$CONFIG_FILE" << EOF
{
  "rpc_url": "https://mainnet.base.org",
  "chain_id": 8453,
  "usdc_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "gateway_url": "https://gateway.apiosk.com",
  "daily_limit_usdc": 100.0,
  "per_request_limit_usdc": 1.0
}
EOF

echo ""
echo "✅ Wallet created successfully!"
echo ""
echo "📍 Address: $ADDRESS"
echo "📂 Saved to: $WALLET_FILE (chmod 600, user-only)"
echo ""
echo "⚠️  SECURITY:"
echo "  Your private key is stored in $WALLET_FILE"
echo "  This file is readable only by you (chmod 600)."
echo "  Only fund this wallet with small amounts for testing (\$1-10)."
echo "  For production, use a hardware wallet or external KMS."
echo ""
echo "💰 Fund your wallet with USDC on Base mainnet:"
echo "  1. Bridge USDC to Base: https://bridge.base.org"
echo "  2. Or buy on Coinbase → Withdraw to Base"
echo "  3. Send to: $ADDRESS"
echo ""
echo "Check balance: ./check-balance.sh"
echo ""
