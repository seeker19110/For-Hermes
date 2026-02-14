#!/usr/bin/env bash
# Flux CLI helper

FLUX_URL="${FLUX_URL:-http://localhost:3000}"

# Helper function for API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3

    if [[ -n "$data" ]]; then
        curl -s -X "$method" "${FLUX_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "${FLUX_URL}${endpoint}" \
            -H "Content-Type: application/json"
    fi
}

# Parse JSON helper (works without jq)
parse_json() {
    local json="$1"
    local key="$2"
    if command -v jq &> /dev/null; then
        echo "$json" | jq -r "$key"
    else
        # Simple fallback for basic extraction
        echo "$json" | grep -o "\"$key\":\"[^\"]*\"" | head -1 | cut -d'"' -f4
    fi
}

# Format JSON output (pretty print if jq available)
format_output() {
    if command -v jq &> /dev/null; then
        jq '.'
    else
        cat
    fi
}

# Commands
case "${1:-}" in
    publish)
        stream="$2"
        source="$3"
        entity_id="$4"
        properties="$5"

        if [[ -z "$stream" || -z "$source" || -z "$entity_id" || -z "$properties" ]]; then
            echo "Usage: flux.sh publish STREAM SOURCE ENTITY_ID PROPERTIES_JSON"
            echo ""
            echo "Example:"
            echo "  flux.sh publish sensors agent-01 temp-sensor-01 '{\"temperature\":22.5}'"
            exit 1
        fi

        timestamp=$(date +%s)000  # Unix epoch milliseconds

        payload=$(cat <<EOF
{
  "entity_id": "${entity_id}",
  "properties": ${properties}
}
EOF
)

        event=$(cat <<EOF
{
  "stream": "${stream}",
  "source": "${source}",
  "timestamp": ${timestamp},
  "payload": ${payload}
}
EOF
)

        echo "Publishing event to Flux..."
        api_call POST "/api/events" "$event" | format_output
        ;;

    batch)
        events="$2"

        if [[ -z "$events" ]]; then
            echo "Usage: flux.sh batch EVENTS_JSON_ARRAY"
            echo ""
            echo "Example:"
            echo '  flux.sh batch '"'"'[{"stream":"sensors","source":"agent-01","payload":{"entity_id":"sensor-01","properties":{"temp":22}}}]'"'"''
            exit 1
        fi

        batch_payload=$(cat <<EOF
{
  "events": ${events}
}
EOF
)

        echo "Publishing batch to Flux..."
        api_call POST "/api/events/batch" "$batch_payload" | format_output
        ;;

    get)
        entity_id="$2"

        if [[ -z "$entity_id" ]]; then
            echo "Usage: flux.sh get ENTITY_ID"
            echo ""
            echo "Example:"
            echo "  flux.sh get temp-sensor-01"
            exit 1
        fi

        api_call GET "/api/state/entities/${entity_id}" | format_output
        ;;

    list)
        api_call GET "/api/state/entities" | format_output
        ;;

    health)
        echo "Testing Flux connection at ${FLUX_URL}..."
        response=$(api_call GET "/api/state/entities")

        if [[ $? -eq 0 && -n "$response" ]]; then
            echo "✓ Flux is reachable"
            entity_count=$(echo "$response" | grep -o '"id"' | wc -l)
            echo "  Entities in state: ${entity_count}"
        else
            echo "✗ Failed to reach Flux at ${FLUX_URL}"
            exit 1
        fi
        ;;

    *)
        echo "Flux CLI - Interact with Flux state engine"
        echo ""
        echo "Usage: flux.sh COMMAND [ARGS]"
        echo ""
        echo "Commands:"
        echo "  publish STREAM SOURCE ENTITY_ID PROPERTIES_JSON"
        echo "      Publish event to create/update entity"
        echo ""
        echo "  get ENTITY_ID"
        echo "      Query current state of entity"
        echo ""
        echo "  list"
        echo "      List all entities in world state"
        echo ""
        echo "  batch EVENTS_JSON_ARRAY"
        echo "      Publish multiple events at once"
        echo ""
        echo "  health"
        echo "      Test connection to Flux"
        echo ""
        echo "Examples:"
        echo "  flux.sh publish sensors agent-01 temp-01 '{\"temperature\":22.5}'"
        echo "  flux.sh get temp-01"
        echo "  flux.sh list"
        echo "  flux.sh health"
        echo ""
        echo "Environment:"
        echo "  FLUX_URL=${FLUX_URL}"
        exit 1
        ;;
esac
