# Security Policy

## Wallet Security

### Private Key Storage

The Apiosk skill generates a standard Ethereum keypair using `ethers.js` and stores it in `~/.apiosk/wallet.json` with restrictive file permissions (chmod 600 — owner read/write only). **The private key is stored in plaintext.**

The private key is required to sign on-chain payment transactions. It is **never transmitted** to the gateway — only your public wallet address is sent with API requests.

**Suitable for:**
- Testing and development
- Small amounts ($1-10 USDC)

**For production, use:**
- Hardware wallet (Ledger, Trezor)
- External KMS (AWS KMS, Google Cloud KMS, HashiCorp Vault)

### Dependencies

Wallet generation uses `ethers.js` (installed via npm from package.json). **No external installers or `curl | bash` required.**

### Network Security

The skill communicates only with:
- `https://gateway.apiosk.com` — Apiosk API gateway (HTTPS only)

### Best Practices

1. **Start small:** Fund with $1-5 USDC for testing
2. **Monitor usage:** Run `./usage-stats.sh` regularly
3. **Dedicated wallet:** Don't reuse wallets from other services
4. **Backup:** Keep a secure backup of `~/.apiosk/wallet.json`
5. **Never share** your private key with anyone

### Reporting Security Issues

Email: olivier@walhallah.com  
Subject: `[SECURITY] Apiosk Skill Vulnerability`

Please do NOT open public GitHub issues for security vulnerabilities.

### License

MIT — Use at your own risk.
