# Apiosk AgentSkill

**Keyless API access with USDC micropayments for OpenClaw agents.**

Pay-per-request for production APIs. No API keys. No accounts. Just pay and call.

---

## 🚀 Quick Start

```bash
# Install via ClawHub
clawhub install apiosk

# Or clone manually
git clone https://github.com/apiosk/apiosk-skill ~/.openclaw/skills/apiosk
cd ~/.openclaw/skills/apiosk

# Setup wallet (one-time)
./setup-wallet.sh

# Fund your wallet with USDC on Base mainnet
# https://bridge.base.org

# List available APIs
./list-apis.sh

# Call an API
./call-api.sh weather --params '{"city": "Amsterdam"}'
```

---

## 📚 Documentation

See [SKILL.md](./SKILL.md) for complete documentation:
- Configuration
- Available APIs
- Usage examples (Node.js, Python, bash)
- Helper scripts
- Troubleshooting

---

## 🔐 Security

- **Proper Ethereum keypair** — generated locally via `ethers.js` (standard, audited library)
- **No external installers** — `npm install` only, no `curl | bash`
- **Private key never transmitted** — only your public address is sent to the gateway
- **Restrictive permissions** — wallet file is chmod 600 (owner-only)
- **HTTPS only** — all gateway communication is encrypted

⚠️ Private key is stored in plaintext locally. Only fund with small amounts for testing. For production, use a hardware wallet or KMS.

See [SECURITY.md](./SECURITY.md) for full details.

---

## 🔧 Gateway Changes Needed

See [GATEWAY_CHANGES_NEEDED.md](./GATEWAY_CHANGES_NEEDED.md) for:
- Required API endpoints
- Database migrations
- Implementation guide

**TL;DR:** Gateway needs 3 new endpoints:
1. `GET /v1/apis` - List available APIs
2. `GET /v1/balance` - Check wallet balance
3. `GET /v1/usage` - Usage statistics

---

## 📦 Files

```
apiosk-skill/
├── SKILL.md                    # Main documentation
├── README.md                   # This file
├── GATEWAY_CHANGES_NEEDED.md   # Implementation guide
├── package.json                # NPM metadata
├── setup-wallet.sh             # Wallet setup (one-time)
├── list-apis.sh                # List available APIs
├── call-api.sh                 # Call any API
├── check-balance.sh            # Check USDC balance
├── usage-stats.sh              # View usage stats
├── apiosk-client.js            # Node.js wrapper
└── apiosk_client.py            # Python wrapper
```

---

## 🎯 What This Enables

**For Agents:**
- Access 15+ production APIs after one-time wallet setup
- Pay per request ($0.001-0.10)
- No API key management
- Automatic USDC micropayments

**For Developers:**
- Monetize any API via Apiosk
- 90-95% revenue share
- No payment processing
- Instant settlement

**Network effect:** More APIs → More agents → More revenue → More APIs

---

## 🌐 Links

- **Website:** https://apiosk.com
- **Dashboard:** https://dashboard.apiosk.com
- **Docs:** https://docs.apiosk.com
- **ClawHub:** https://clawhub.com/apiosk
- **Moltbook:** @ApioskAgent

---

## 🦞 About

Built by Apiosk for the agent economy.

**Mission:** Make every API instantly accessible to every agent.

---

## 📝 License

MIT
