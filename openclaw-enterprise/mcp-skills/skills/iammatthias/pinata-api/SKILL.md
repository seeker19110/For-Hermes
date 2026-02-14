# Pinata API Skill

Interact with Pinata's IPFS storage services for file management, groups, gateways, signatures, payments, and AI-powered vector search.

Repo: https://github.com/PinataCloud/pinata-api-skill

## Setup

Set the following environment variables:

- `PINATA_JWT` (required) - Your Pinata API JWT token
- `GATEWAY_URL` (required) - Your Pinata gateway domain (e.g., `your-gateway.mypinata.cloud`)
- `GATEWAY_KEY` (optional) - Gateway key for accessing public IPFS content not tied to your Pinata account. Required when fetching content from the broader IPFS network. See [Gateway Access Controls](https://docs.pinata.cloud/gateways/gateway-access-controls#gateway-keys)

## Available Functions

### Authentication

- `testAuthentication()` - Verify your Pinata JWT is valid

### Files

- `searchFiles({ network?, name?, cid?, mimeType?, limit?, pageToken? })` - Search files
- `getFileById({ network?, id })` - Get file by ID
- `updateFile({ network?, id, name?, keyvalues? })` - Update file metadata
- `deleteFile({ network?, id })` - Delete a file
- `uploadFile({ file, fileName, network?, group_id?, keyvalues? })` - Upload a file

### Groups

- `listGroups({ network?, name?, limit?, pageToken? })` - List groups
- `createGroup({ network?, name })` - Create a group
- `getGroup({ network?, id })` - Get group by ID
- `updateGroup({ network?, id, name })` - Update group
- `deleteGroup({ network?, id })` - Delete a group
- `addFileToGroup({ network?, groupId, fileId })` - Add file to group
- `removeFileFromGroup({ network?, groupId, fileId })` - Remove file from group

### Gateway & Downloads

- `createPrivateDownloadLink({ cid, expires? })` - Create temporary download link
- `createSignedUploadUrl({ expires, max_file_size?, allow_mime_types?, group_id?, filename?, keyvalues? })` - Create signed upload URL for client-side uploads

### Signatures

- `addSignature({ network?, cid, signature, address })` - Add EIP-712 signature
- `getSignature({ network?, cid })` - Get signature for CID
- `deleteSignature({ network?, cid })` - Delete signature

### Pin By CID

- `pinByCid({ cid, name?, group_id?, keyvalues?, host_nodes? })` - Pin existing IPFS content
- `queryPinRequests({ order?, status?, cid?, limit?, pageToken? })` - Query pin request status
- `cancelPinRequest({ id })` - Cancel pending pin request

### x402 Payment Instructions

- `createPaymentInstruction({ name, pay_to, amount_usdc, network?, description? })` - Create payment instruction
- `listPaymentInstructions({ limit?, pageToken?, cid?, name?, id? })` - List payment instructions
- `getPaymentInstruction({ id })` - Get payment instruction
- `deletePaymentInstruction({ id })` - Delete payment instruction
- `addCidToPaymentInstruction({ id, cid })` - Associate CID with payment
- `removeCidFromPaymentInstruction({ id, cid })` - Remove CID from payment

### Vectorize (AI Search)

- `vectorizeFile({ file_id })` - Generate vector embeddings for a file
- `deleteFileVectors({ file_id })` - Delete vectors for a file
- `queryVectors({ group_id, text })` - Semantic search within a group

## Parameters

- `network` - IPFS network: `"public"` (default) or `"private"`
- `amount_usdc` - USD amount as string (e.g., `"1.50"` for $1.50)
- `blockchain network` - For payments: `"base"` (default) or `"base-sepolia"`
