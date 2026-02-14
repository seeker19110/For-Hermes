# Xerolite REST API Reference

This document describes the Xerolite API endpoints used by the skill CLI (`scripts/xerolite.mjs`).

## Base Configuration

- **Base URL**: `XEROLITE_API_URL` (e.g. `https://your-xerolite-host` — host only, no `/api` suffix; the script appends the path).
- **Authentication**: Optional Bearer token via `XEROLITE_API_KEY`. If set, the CLI sends `Authorization: Bearer <key>`.

## Endpoints

### Place order

- **Path**: `POST /api/agent/order/place-order`
- **Used by**: `node xerolite.mjs order place ...`

Request body (required: `action`, `qty`, `symbol`; optional with defaults: `currency`, `asset_class`, `exch`):

```json
{
  "name": "Agent",
  "action": "BUY",
  "qty": "10",
  "symbol": "AAPL",
  "currency": "USD",
  "asset_class": "STOCK",
  "exch": "SMART"
}
```

### Contract search

- **Path**: `POST /api/agent/contract/search`
- **Used by**: `node xerolite.mjs contract search ...`

Request body (required: `symbol`; optional with defaults: `currency`, `xeroAssetClass`; script sends fixed `brokerName: "IBKR"`):

```json
{
  "brokerName": "IBKR",
  "symbol": "AAPL",
  "currency": "USD",
  "xeroAssetClass": "STOCK"
}
```

### Defaults (CLI)

When flags are omitted, the script uses: `currency=USD`, `asset-class=STOCK`, `exch=SMART`.

### Response Format

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 400  | Bad Request |
| 401  | Unauthorized |
| 404  | Not Found |
| 500  | Server Error |
