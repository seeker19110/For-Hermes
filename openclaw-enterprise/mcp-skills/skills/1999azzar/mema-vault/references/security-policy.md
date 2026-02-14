# Mema Vault: Security Policy

## Core Principle
- **Zero Trust**: Assume the environment is hostile.
- **Encrypt Everything**: All stored secrets must be AES-256-GCM encrypted.
- **Minimal Access**: Only decrypt what is needed, when it is needed.

## Key Management
- Master Key is **never** stored in plaintext.
- Use `keyring` or `os.environ` to retrieve Master Key.
- Rotate keys every 90 days.

## Data Structure (Redis/JSON)
```json
{
  "service": "AWS",
  "account": "root",
  "ciphertext": "U2FsdGVkX1+...",
  "iv": "...",
  "meta": {
    "updated_at": 1678886400,
    "version": 1
  }
}
```

## Audit Logging
- Every access (read/write) must be logged.
- Log **who** accessed **what**, but **never** log the secret itself.
