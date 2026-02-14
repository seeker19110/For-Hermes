---
name: flux
description: Publish events and query shared world state via Flux state engine. Use when agents need to share observations, coordinate on shared data, or track entity state across systems.
---

# Flux Skill

Flux is a persistent, shared, event-sourced world state engine. Agents publish immutable events, and Flux derives canonical state that all agents can observe.

## Key Concepts

- **Events**: Immutable observations (temperature readings, status changes, etc.)
- **Entities**: State objects derived from events (sensors, devices, agents)
- **Properties**: Key-value attributes of entities
- **Streams**: Logical event namespaces (sensors, agents, system)

## Prerequisites

**Flux Instance:**
- Default: `http://localhost:3000` (local instance)
- Can override with: `export FLUX_URL=https://your-flux-url.com`

**Options:**
1. Run Flux locally (see [Flux repo](https://github.com/EckmanTechLLC/flux))
2. Use public test instance: `https://deutschland-jackie-substantially-pee.trycloudflare.com`
3. Deploy your own Flux instance

No authentication required (current setup).

## Testing

Verify Flux connection:
```bash
./scripts/flux.sh health
```

## Scripts

Use the provided bash script in the `scripts/` directory:
- `flux.sh` - Main CLI tool

## Common Operations

### Publish Event
```bash
./scripts/flux.sh publish <stream> <source> <entity_id> <properties_json>

# Example: Publish sensor reading
./scripts/flux.sh publish sensors agent-01 temp-sensor-01 '{"temperature":22.5,"unit":"celsius"}'
```

### Query Entity State
```bash
./scripts/flux.sh get <entity_id>

# Example: Get current sensor state
./scripts/flux.sh get temp-sensor-01
```

### List All Entities
```bash
./scripts/flux.sh list

# Shows all entities in current world state
```

### Batch Publish Events
```bash
./scripts/flux.sh batch '[
  {"stream":"sensors","source":"agent-01","payload":{"entity_id":"sensor-01","properties":{"temp":22}}},
  {"stream":"sensors","source":"agent-01","payload":{"entity_id":"sensor-02","properties":{"temp":23}}}
]'
```

## Use Cases

### Multi-Agent Coordination
Agents publish observations to shared entities:
```bash
# Agent A observes temperature
flux.sh publish sensors agent-a room-101 '{"temperature":22.5}'

# Agent B queries current state
flux.sh get room-101
# Returns: {"temperature":22.5,...}
```

### Status Tracking
Track service/system state:
```bash
# Publish status change
flux.sh publish system monitor api-gateway '{"status":"healthy","uptime":3600}'

# Query current status
flux.sh get api-gateway
```

### Event Sourcing
All state changes are event-sourced:
- Events are immutable (never deleted/modified)
- State derived from event history
- Can replay/audit full history

## API Endpoints

- `POST /api/events` - Publish single event
- `POST /api/events/batch` - Publish multiple events
- `GET /api/state/entities` - List all entities
- `GET /api/state/entities/:id` - Get specific entity

See `references/api.md` for full API documentation.

## Notes

- Events auto-generate UUIDs (no need to provide eventId)
- Properties merge on updates (last write wins per property)
- State persists in Flux (survives restarts via NATS JetStream)
- Timestamp defaults to current time if not provided
