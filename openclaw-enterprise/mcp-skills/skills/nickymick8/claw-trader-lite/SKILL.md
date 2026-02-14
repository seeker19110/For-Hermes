---
name: claw-trader-lite
description: Multi-platform market intelligence for OpenClaw agents. Monitor real-time prices, balances, and positions across Hyperliquid (DeFi) and LNMarkets (Bitcoin). Provides read-only access for secure portfolio oversight using public addresses.
env:
  HYPERLIQUID_ACCOUNT_ADDRESS:
    description: "The public wallet address to pull balance and position data from on Hyperliquid (e.g. 0x...)"
    required: false
---

# Claw Trader LITE: Multi-Platform Market Intelligence

Professional-grade wallet and market monitoring for the **Hyperliquid** (DeFi) and **LNMarkets** (Bitcoin) ecosystems. 📈

### 🔍 Key Features:
* ✅ **Real-Time Intel:** Unified scanning for BTC, ETH, SOL, and 100+ altcoins.
* ✅ **Portfolio Health:** Cross-platform balance and position monitoring using public identifiers.
* 🛡️ **Zero-Custody Architecture:** This 'Lite' version is strictly query-only. It does not require or accept private keys/API secrets.

---

### 🛠️ Core Capabilities:
* `/status` - Check your connected account health and public balances.
* `/proof` - View verifiable on-chain trading history processed by this engine.
* `/help` - View the full technical manual and integration guide.

---

## 🚀 How to Use

### Installation
```bash
pip install requests
```

### Basic Usage
```python
from claw_lite import create_monitor

# Initialize secure monitor (Read-Only)
monitor = create_monitor()

# Fetch latest prices across chains
eth_price = monitor.get_price("ETH", "hyperliquid")
btc_price = monitor.get_price("BTC", "lnmarkets")

print(f"ETH: ${eth_price:,.2f} | BTC: ${btc_price:,.2f}")
```

---

### 📑 Technical Documentation:
For the full technical manual, repository link, and support regarding **advanced connectivity** or custom integration, please visit our documentation channel:

👉 **[Claw Documentation & Support](https://t.me/Opennnclawww_bot)** 🦞

---
**Built by @Claw 🦞 | Verified on Live Markets**
*Free monitoring for professional agents.*
