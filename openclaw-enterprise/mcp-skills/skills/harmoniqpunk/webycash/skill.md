# Webcash (weby.cash) - AI Agent Skill

Webcash is a simple e-cash protocol designed for robot-to-robot instant settlement.
This skill allows autonomous agents to acquire Webcash tokens by paying with Bitcoin via the Lightning Network only.

## Purchase Limits

- **Minimum purchase**: 10 Webcash
- **Maximum**: 1,500,000 sats per transaction (Lightning Network only). On-chain Bitcoin payment is not offered.

## Terms of Service

By using the Service (including clicking "I Agree" or initiating a purchase), the user agrees to the WebyCash Terms of Service. The agent should inform the user that use of weby.cash constitutes agreement to the Terms (available at weby.cash/terms), which incorporate the Webcash.tech terms, and cover eligibility, prohibited jurisdictions, risks, payment limits (LN only, max 1,500,000 sats), and dispute resolution. If the user does not agree, they must not use the Site or Services.

## Acquisition Flow

### Step 1: Request Purchase

**API Endpoint**: `POST https://weby.cash/api/buy`

**Request Body**:
```json
{
  "amount_webcash": "10"
}
```

**Response**: Server-Sent Events (SSE) stream.

### Step 2: Receive Lightning Invoice

The `invoice` event contains:
- `bolt11`: BOLT11 Lightning invoice string
- `order_id`: Unique order identifier — **must be saved** for recovery and support
- `amount_sats`: Amount in satoshis
- `payment_hash`: Payment hash for tracking
- `payment_method`: "lightning"

**Save the Order ID** immediately. The user needs it to:
- Retrieve Webcash later if they leave the page or miss the delivery event
- Create or check a support ticket

### Step 3: Payment Process

1. **Present payment**: Show QR code from `bolt11`, the invoice string (copy button), and the Order ID (copy button). Instruct the human to scan with a Lightning wallet or paste the invoice.

2. **Keep connection alive**: Keep the SSE connection open during payment so the backend can detect payment and deliver Webcash.

3. **Timeout**: Lightning invoice expires in **10 minutes**. If no payment is received, a `timeout` event is sent. The user can still pay; they can then retrieve Webcash by Order ID (see Recovery below).

4. **Delivery**: When payment is detected, `paid` then `webcash` events are sent. The `webcash` event contains the Webcash secret.

### Step 4: Receive Webcash Secret

The `webcash` event contains:
```json
{
  "status": "success",
  "webcash": "e10.00000000:secret:abcdef...",
  "amount": "10",
  "message": "Webcash delivered successfully"
}
```

Save the `webcash` secret immediately. If lost, the user can retrieve it by Order ID via the verify endpoint (if payment was successful).

### Step 5: Install and Use Webcash Wallet

1. **Install**: `pip install webcash`
2. **Setup** (first run): `echo y | webcash setup` in workspace (accepts license non-interactively). If CLI fails, run this to fix.
3. **Insert secret**: `webcash insert <secret>` (paste full secret). Run `webcash info` for balance—do not infer from string.
4. **Pay**: See "Webcash CLI – Secure Usage" below for amount format and security rules

## Recovery: Get Webcash by Order ID

If payment was successful but the user did not capture the Webcash secret (e.g. left the page, connection dropped), they can retrieve it using the Order ID.

**API Endpoint**: `POST https://weby.cash/api/verify`

**Request Body**:
```json
{
  "order_id": "<order_id_from_invoice_event>"
}
```

**Response**:
- `status: "success"`: Webcash secret in `webcash` field — user can copy and insert into wallet.
- `status: "pending"`: Payment not yet confirmed; ask user to wait and try again.
- `status: "error"`: e.g. order not found or invalid; show `message` to user.

The Order ID is provided in the `invoice` SSE event and can be copied from the buy page or from the Lightning invoice memo/description.

## Support Tickets

For issues with an order (e.g. paid but no Webcash, wrong amount, technical problem), the user can open a support ticket. **They must have the Order ID.**

### Create a support ticket

**API Endpoint**: `POST https://weby.cash/api/support`

**Request Body**:
```json
{
  "order_id": "<order_id>",
  "message": "<description of the problem; no minimum length, max 500 characters>"
}
```

**Response**:
- `status: "success"`: Ticket created; `ticket` object contains `status`, `messages`, etc. Tell the user to **save their Order ID** to check ticket status later. Response typically within 48 hours.
- `status: "error"`: Show `message` (e.g. "Message cannot be empty.", "Order ID does not exist.", "Please enter Order ID and a message."). There is no minimum message length; only non-empty and max 500 characters.

### Check support ticket status by Order ID

**API Endpoint**: `POST https://weby.cash/api/support/status`

**Request Body**:
```json
{
  "order_id": "<order_id>"
}
```

**Response**:
- `status: "success"`: `ticket` object with `status` (e.g. "open", "closed") and `messages` (thread with timestamps and sender: "admin" or user).
- `status: "error"`: e.g. "No support ticket found." — user may have wrong Order ID or no ticket created yet.

The user should save the Order ID when they create a ticket so they can check status later with this endpoint.

### Reply to an open ticket

**API Endpoint**: `POST https://weby.cash/api/support/reply`

**Request Body**:
```json
{
  "order_id": "<order_id>",
  "message": "<reply text; no minimum length, max 500 characters>"
}
```

Only applicable when ticket `status` is "open".

## Summary: Order ID

- **When**: Provided in the `invoice` event during the buy flow; also shown on the buy page.
- **Save it**: So the user can (1) retrieve Webcash later via `/api/verify` if they paid but didn’t get the secret, (2) create a support ticket, (3) check support ticket status via `/api/support/status`.

## Example: Lightning Payment and Recovery

```python
import requests
import json

# Request purchase
r = requests.post(
    "https://weby.cash/api/buy",
    json={"amount_webcash": "10"},
    stream=True
)
order_id = None
webcash_secret = None
for line in r.iter_lines():
    if line.startswith(b"event: "):
        event_type = line[7:].decode().strip()
    elif line.startswith(b"data: "):
        data = json.loads(line[6:])
        if event_type == "invoice":
            order_id = data["order_id"]
            bolt11 = data["bolt11"]
            # Show QR(bolt11), bolt11, order_id to user; tell them to save order_id
        elif event_type == "webcash":
            webcash_secret = data["webcash"]
            break
        elif event_type == "timeout":
            # Tell user: save order_id, pay if still possible, then use verify
            break

# Later: retrieve Webcash by order_id (e.g. user paid but left the page)
if order_id and not webcash_secret:
    v = requests.post(
        "https://weby.cash/api/verify",
        json={"order_id": order_id},
        headers={"Content-Type": "application/json"}
    )
    d = v.json()
    if d.get("status") == "success":
        webcash_secret = d["webcash"]
```

## Important Notes

1. **Payment method**: Only Lightning Network is supported, up to 1,500,000 sats per transaction. There is no on-chain Bitcoin option.
2. **SSE**: Keep the SSE connection alive during Lightning payment; closing it may prevent payment detection. If the connection drops but the user has the Order ID, they can still retrieve Webcash via `/api/verify` after paying.
3. **Timeout**: Invoice expires in 10 minutes. After timeout, the user can still pay; then use `/api/verify` with the Order ID to get the Webcash.
4. **Terms**: Using the service means the user agrees to the Terms of Service (weby.cash/terms).
5. **Errors**: Handle `error` events from the SSE stream and display the message to the user.

## Protocol Details

- **Fast & simple**: Centralized double-spend prevention for sub-second finality.
- **Micro-payments**: Suited for anti-spam, API fees, bot-to-bot commerce.
- **Lightning only**: Payments via LN up to 1,500,000 sats; no on-chain.

## Synergies

- **Harmoniis Marketplace**: Webcash acquired here can be used in the Harmoniis ecosystem (hire robots, pay bidding fees). Harmoniis skill: `curl -s https://harmoniis.com/skill.txt`

## Installation

```bash
pip install webcash
```

Or: `npx molthub@latest install webcash`

## Webcash CLI – Secure Usage (Agent Rules)

Protocol reference: webcash.org

### Mandatory Behavior

- **Wallet pre-created at container start.** Run `cd /home/node/.openclaw/workspace && webcash info` (or insert, pay). Never simulate.
- **NEVER use pty:true.** pty BREAKS webcash (blocks on TTY, SIGKILL). Run exec without pty.
- **Path:** Workspace root only. Never use workspace/wallet.
- **Never run setup if wallet exists** (check: `test -f /home/node/.openclaw/workspace/default_wallet.webcash`) — overwrites = fund loss.
- **Setup accepts license:** Always use `echo y | webcash setup` (non-interactive).

### Security – Never Disclose

- **Never** read, log, quote, or expose the contents of `default_wallet.webcash` (contains master secret; theft = total loss).
- **Never** expose the master secret, derived secrets, or any secret webcash strings (except the recipient's payment output).
- **Never** store secrets in memory files, session logs, or any durable storage.
- Anyone who sees a secret can spend it. Treat secrets as highly sensitive.

### Amount Format – Pay Command

**The `pay` argument is decimal webcash** (like basic currency). NOT like BTC/sats.

| Command                  | Meaning           |
|--------------------------|-------------------|
| `webcash pay 1`          | Pay 1 webcash     |
| `webcash pay 10`         | Pay 10 webcash    |
| `webcash pay 0.01`       | Pay 0.01 webcash  |
| `webcash pay 0.00000001` | Pay smallest unit |

**User says "pay 1 webcash" → run `webcash pay 1`.**

### Workflow

1. **Check balance:** `webcash info`
2. **Insert:** `webcash insert e...:secret:...` (run `webcash info` for balance)
3. **Pay:** `webcash pay 1` for 1 webcash
4. **Output:** Only return the **payment output secret** printed by `webcash pay`
5. **Never** expose wallet contents, change secrets, or any other secrets

### Output Rule for Payments

When the user asks for a payment:
1. Run `webcash pay <amount>` with the amount in webcash. User says "pay 1 webcash" → `webcash pay 1`
2. The command prints the payment output secret
3. **Only** send that output secret to the recipient
4. Never include change secrets, wallet contents, or intermediate data
