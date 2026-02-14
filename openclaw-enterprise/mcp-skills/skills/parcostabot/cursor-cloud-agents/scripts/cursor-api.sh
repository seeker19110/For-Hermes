#!/usr/bin/env bash
#
# cursor-api.sh - Cursor Cloud Agents API wrapper for OpenClaw
#
# Usage: cursor-api.sh <command> [options] [args]
#
# Commands:
#   list              List all agents
#   launch            Launch a new agent
#   status <id>       Get agent status
#   conversation <id> Get agent conversation history
#   followup <id>     Send follow-up message to agent
#   stop <id>         Stop an agent
#   delete <id>       Delete an agent
#   models            List available models
#   me                Get account information
#   verify <repo>     Verify repository access
#   usage             Get usage/cost information
#
# Environment:
#   CURSOR_API_KEY    Required. Your Cursor API key (auto-detected from
#                     ~/.openclaw/.env, ~/.openclaw/.env.local, .env, or
#                     ~/.cursor/config.json if not set)
#   CURSOR_API_BASE   Optional. API base URL override for testing
#                     (default: https://api.cursor.com/v0)
#   CURSOR_CACHE_TTL  Optional. Cache TTL in seconds (default: 60)
#
# Exit codes:
#   0  Success
#   1  API error
#   2  Authentication missing
#   3  Rate limited
#   4  Repository not accessible
#   5  Invalid arguments

set -euo pipefail

# Configuration
readonly API_BASE="${CURSOR_API_BASE:-https://api.cursor.com/v0}"
readonly CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/cursor-api"
readonly CACHE_TTL="${CURSOR_CACHE_TTL:-60}"
readonly RATE_LIMIT_FILE="${CACHE_DIR}/.last_request"
readonly RATE_LIMIT_DELAY=1  # 1 request per second
readonly CURL_CONNECT_TIMEOUT=10
readonly CURL_MAX_TIME=120
readonly CURL_RETRY_COUNT=3

# Global flags
USE_CACHE=true
VERBOSE=false

# Exit codes
readonly E_API_ERROR=1
readonly E_AUTH_MISSING=2
readonly E_RATE_LIMITED=3
readonly E_REPO_INACCESSIBLE=4
readonly E_INVALID_ARGS=5

#######################################
# Utility Functions
#######################################

# Strip quotes from a string
strip_quotes() {
    local str="$1"
    # Remove leading and trailing double quotes
    str="${str#\"}"
    str="${str%\"}"
    # Remove leading and trailing single quotes
    # shellcheck disable=SC2016  # Intentional single quote pattern
    str="${str#'}"
    str="${str%'}"
    echo "$str"
}

# Get API key from various sources
get_api_key() {
    local key

    # Check environment variable first
    if [[ -n "${CURSOR_API_KEY:-}" ]]; then
        verbose "Using CURSOR_API_KEY from environment"
        echo "$CURSOR_API_KEY"
        return 0
    fi

    # Check ~/.openclaw/.env
    if [[ -f "$HOME/.openclaw/.env" ]]; then
        key=$(grep -E '^CURSOR_API_KEY=' "$HOME/.openclaw/.env" | cut -d= -f2-)
        key=$(strip_quotes "$key")
        if [[ -n "$key" ]]; then
            verbose "Using CURSOR_API_KEY from ~/.openclaw/.env"
            echo "$key"
            return 0
        fi
    fi

    # Check ~/.openclaw/.env.local
    if [[ -f "$HOME/.openclaw/.env.local" ]]; then
        key=$(grep -E '^CURSOR_API_KEY=' "$HOME/.openclaw/.env.local" | cut -d= -f2-)
        key=$(strip_quotes "$key")
        if [[ -n "$key" ]]; then
            verbose "Using CURSOR_API_KEY from ~/.openclaw/.env.local"
            echo "$key"
            return 0
        fi
    fi

    # Check .env in current directory
    if [[ -f ".env" ]]; then
        key=$(grep -E '^CURSOR_API_KEY=' ".env" | cut -d= -f2-)
        key=$(strip_quotes "$key")
        if [[ -n "$key" ]]; then
            verbose "Using CURSOR_API_KEY from .env"
            echo "$key"
            return 0
        fi
    fi

    # Check ~/.cursor/config.json (Cursor config file)
    if [[ -f "$HOME/.cursor/config.json" ]]; then
        key=$(jq -r '.apiKey // empty' "$HOME/.cursor/config.json" 2>/dev/null)
        if [[ -n "$key" && "$key" != "null" ]]; then
            verbose "Using API key from ~/.cursor/config.json"
            echo "$key"
            return 0
        fi
    fi

    return 1
}

# Print error message to stderr
error() {
    echo "{\"error\": \"$1\", \"code\": ${2:-$E_API_ERROR}}" >&2
    exit "${2:-$E_API_ERROR}"
}

# Print verbose message
verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "[VERBOSE] $1" >&2
    fi
}

# Sanitize input to prevent command injection
sanitize_id() {
    local id="$1"
    # Only allow alphanumeric, hyphens, and underscores
    if [[ ! "$id" =~ ^[a-zA-Z0-9_-]+$ ]]; then
        error "Invalid ID format: $id" "$E_INVALID_ARGS"
    fi
    echo "$id"
}

sanitize_repo() {
    local repo="$1"
    # Allow owner/repo format with alphanumeric, hyphens, underscores, dots
    if [[ ! "$repo" =~ ^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$ ]]; then
        error "Invalid repository format: $repo (expected: owner/repo)" "$E_INVALID_ARGS"
    fi
    echo "$repo"
}

#######################################
# Rate Limiting
#######################################

# Enforce rate limiting (1 request per second)
rate_limit() {
    if [[ -f "$RATE_LIMIT_FILE" ]]; then
        local last_request now delta
        last_request=$(cat "$RATE_LIMIT_FILE" 2>/dev/null || echo 0)
        now=$(date +%s)
        delta=$((now - last_request))

        if [[ $delta -lt $RATE_LIMIT_DELAY ]]; then
            local sleep_time=$((RATE_LIMIT_DELAY - delta))
            verbose "Rate limiting: sleeping for ${sleep_time}s"
            sleep "$sleep_time"
        fi
    fi

    # Update last request time
    mkdir -p "$CACHE_DIR"
    date +%s > "$RATE_LIMIT_FILE"
}

#######################################
# Caching
#######################################

# Get cache key for a request
cache_key() {
    local endpoint="$1"
    echo "${CACHE_DIR}/$(echo "$endpoint" | tr '/' '_').json"
}

# Check if cached response is valid
cache_valid() {
    local cache_file="$1"

    if [[ "$USE_CACHE" != "true" ]]; then
        return 1
    fi

    if [[ ! -f "$cache_file" ]]; then
        return 1
    fi

    local now cache_time age
    now=$(date +%s)
    cache_time=$(stat -f %m "$cache_file" 2>/dev/null || stat -c %Y "$cache_file" 2>/dev/null || echo 0)
    age=$((now - cache_time))

    if [[ $age -gt $CACHE_TTL ]]; then
        return 1
    fi

    return 0
}

# Read from cache
read_cache() {
    local cache_file="$1"
    if cache_valid "$cache_file"; then
        verbose "Cache hit: $cache_file"
        cat "$cache_file"
        return 0
    fi
    return 1
}

# Write to cache
write_cache() {
    local cache_file="$1"
    local data="$2"

    mkdir -p "$CACHE_DIR"
    echo "$data" > "$cache_file"
}

# Clear all cache
clear_cache() {
    if [[ -d "$CACHE_DIR" ]]; then
        rm -rf "${CACHE_DIR:?}"/*
        echo '{"status": "cache_cleared"}'
    fi
}

#######################################
# Authentication
#######################################

# Check if API key is configured
check_auth() {
    local api_key
    api_key=$(get_api_key) || error "CURSOR_API_KEY not found. Set it in: environment variable, ~/.openclaw/.env, ~/.openclaw/.env.local, or .env file" "$E_AUTH_MISSING"
}

# Get authorization header
get_auth_header() {
    local api_key credentials
    api_key=$(get_api_key) || return 1
    credentials="${api_key}:"
    echo "Authorization: Basic $(printf '%s' "$credentials" | base64)"
}

#######################################
# API Functions
#######################################

# Make API request with retry logic
api_request() {
    local method="$1"
    local endpoint="$2"
    local body="${3:-}"
    local use_cache="${4:-false}"

    check_auth

    local cache_file
    cache_file=$(cache_key "$endpoint")

    # Try cache for GET requests
    if [[ "$method" == "GET" && "$use_cache" == "true" ]]; then
        if read_cache "$cache_file"; then
            return 0
        fi
    fi

    # Apply rate limiting
    rate_limit

    local curl_opts=(
        -s
        -w "\n%{http_code}"
        --connect-timeout "$CURL_CONNECT_TIMEOUT"
        --max-time "$CURL_MAX_TIME"
    )
    local headers=(-H "Content-Type: application/json" -H "$(get_auth_header)")
    local url="${API_BASE}${endpoint}"

    verbose "API Request: $method $url"

    local response http_code curl_stderr
    local attempt=1
    local retry_delay=2

    while [[ $attempt -le $CURL_RETRY_COUNT ]]; do
        curl_stderr=$(mktemp)

        if [[ "$method" == "GET" ]]; then
            response=$(curl "${curl_opts[@]}" "${headers[@]}" "$url" 2>"$curl_stderr") || {
                error "curl failed: $(cat "$curl_stderr")" "$E_API_ERROR"
            }
        else
            if [[ -n "$body" ]]; then
                response=$(curl "${curl_opts[@]}" "${headers[@]}" -X "$method" -d "$body" "$url" 2>"$curl_stderr") || {
                    error "curl failed: $(cat "$curl_stderr")" "$E_API_ERROR"
                }
            else
                response=$(curl "${curl_opts[@]}" "${headers[@]}" -X "$method" "$url" 2>"$curl_stderr") || {
                    error "curl failed: $(cat "$curl_stderr")" "$E_API_ERROR"
                }
            fi
        fi

        rm -f "$curl_stderr"

        # Extract HTTP code and body
        http_code=$(echo "$response" | tail -n1)
        response=$(echo "$response" | sed '$d')

        verbose "HTTP Code: $http_code (attempt $attempt)"

        # Check if we should retry
        if [[ "$http_code" == "429" ]] || [[ "$http_code" =~ ^5 ]]; then
            if [[ $attempt -lt $CURL_RETRY_COUNT ]]; then
                verbose "Retrying in ${retry_delay}s..."
                sleep "$retry_delay"
                retry_delay=$((retry_delay * 2))  # Exponential backoff
                ((attempt++))
                continue
            fi
        fi

        break
    done

    # Handle HTTP errors
    case "$http_code" in
        200|201)
            # Success
            ;;
        401)
            error "Authentication failed - invalid CURSOR_API_KEY" "$E_AUTH_MISSING"
            ;;
        403)
            error "Forbidden - check repository access" "$E_REPO_INACCESSIBLE"
            ;;
        404)
            error "Resource not found" "$E_API_ERROR"
            ;;
        429)
            error "Rate limited by API" "$E_RATE_LIMITED"
            ;;
        400)
            # Handle 400 errors with API error details
            # Provide more context if available in response
            if echo "$response" | jq -e '.error' >/dev/null 2>&1; then
                local api_error
                api_error=$(echo "$response" | jq -r '.error')
                error "API error: $api_error (HTTP 400)" "$E_API_ERROR"
            else
                error "API error: Bad request (HTTP 400)" "$E_API_ERROR"
            fi
            ;;
        4*|5*)
            error "API error: HTTP $http_code" "$E_API_ERROR"
            ;;
        *)
            error "Unexpected response: HTTP $http_code" "$E_API_ERROR"
            ;;
    esac

    # Validate JSON response
    if ! echo "$response" | jq empty 2>/dev/null; then
        error "Invalid JSON response from API" "$E_API_ERROR"
    fi

    # Cache successful GET responses
    if [[ "$method" == "GET" && "$use_cache" == "true" ]]; then
        write_cache "$cache_file" "$response"
    fi

    echo "$response"
}

#######################################
# Command Implementations
#######################################

# List all agents
cmd_list() {
    local limit=""
    local offset=""
    local query_params=""

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --limit)
                limit="$2"
                shift 2
                ;;
            --offset)
                offset="$2"
                shift 2
                ;;
            *)
                error "Unknown option: $1" "$E_INVALID_ARGS"
                ;;
        esac
    done

    # Build query string if pagination params provided
    if [[ -n "$limit" || -n "$offset" ]]; then
        query_params="?"
        [[ -n "$limit" ]] && query_params+="limit=${limit}"
        [[ -n "$limit" && -n "$offset" ]] && query_params+="&"
        [[ -n "$offset" ]] && query_params+="offset=${offset}"
    fi

    api_request "GET" "/agents${query_params}" "" "true"
}

# Launch a new agent
cmd_launch() {
    local repo=""
    local prompt=""
    local model=""
    local branch=""
    local auto_create_pr=true

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --repo)
                repo="$2"
                shift 2
                ;;
            --prompt)
                prompt="$2"
                shift 2
                ;;
            --model)
                model="$2"
                shift 2
                ;;
            --branch)
                branch="$2"
                shift 2
                ;;
            --no-pr)
                auto_create_pr=false
                shift
                ;;
            *)
                error "Unknown option: $1" "$E_INVALID_ARGS"
                ;;
        esac
    done

    if [[ -z "$repo" ]]; then
        error "Repository required (--repo owner/repo)" "$E_INVALID_ARGS"
    fi

    if [[ -z "$prompt" ]]; then
        error "Prompt required (--prompt \"...\")" "$E_INVALID_ARGS"
    fi

    repo=$(sanitize_repo "$repo")

    # Use default model if not specified
    if [[ -z "$model" ]]; then
        model="gpt-5.2"
        verbose "No model specified, using default: $model"
        echo "Using default model: $model (specify --model to override)" >&2
    else
        verbose "Using specified model: $model"
        echo "Using model: $model" >&2
    fi

    # Build request body using jq
    # API expects: source.repository (full URL), prompt.text (object)
    local body
    body=$(jq -n \
        --arg repo "github.com/$repo" \
        --arg prompt "$prompt" \
        --arg model "$model" \
        '{source: {repository: $repo}, prompt: {text: $prompt}, model: $model}')

    [[ -n "$branch" ]] && body=$(echo "$body" | jq --arg b "$branch" '.target.branchName = $b')
    [[ "$auto_create_pr" == "true" ]] && body=$(echo "$body" | jq '.target.autoCreatePr = true')

    api_request "POST" "/agents" "$body"
}

# Get agent status
cmd_status() {
    local agent_id
    agent_id=$(sanitize_id "$1")
    api_request "GET" "/agents/${agent_id}" "" "true"
}

# Get agent conversation
cmd_conversation() {
    local agent_id
    agent_id=$(sanitize_id "$1")
    api_request "GET" "/agents/${agent_id}/conversation" "" "true"
}

# Send follow-up message
cmd_followup() {
    local agent_id
    agent_id=$(sanitize_id "$1")
    shift

    # Check agent state before attempting followup
    local agent_status
    agent_status=$(api_request "GET" "/agents/${agent_id}" "" "false" 2>/dev/null | jq -r '.status // empty' 2>/dev/null || echo "")

    if [[ -n "$agent_status" ]]; then
        case "$agent_status" in
            FINISHED|STOPPED|ERROR)
                error "Cannot send followup to agent in '$agent_status' state. Agent must be RUNNING or CREATING." "$E_API_ERROR"
                ;;
            RUNNING|CREATING)
                # OK to proceed
                ;;
            *)
                verbose "Unknown agent status: $agent_status, attempting followup anyway"
                ;;
        esac
    fi

    local prompt=""

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --prompt)
                prompt="$2"
                shift 2
                ;;
            *)
                if [[ -z "$prompt" ]]; then
                    prompt="$1"
                    shift
                else
                    prompt="$prompt $1"
                    shift
                fi
                ;;
        esac
    done

    if [[ -z "$prompt" ]]; then
        error "Prompt required (--prompt or positional arg)" "$E_INVALID_ARGS"
    fi

    local body
    body='{"prompt": '"$(echo "$prompt" | jq -Rs .)"'}'

    api_request "POST" "/agents/${agent_id}/followup" "$body"
}

# Stop an agent
cmd_stop() {
    local agent_id
    agent_id=$(sanitize_id "$1")
    api_request "POST" "/agents/${agent_id}/stop"
}

# Delete an agent
cmd_delete() {
    local agent_id
    agent_id=$(sanitize_id "$1")
    api_request "DELETE" "/agents/${agent_id}"
}

# List models
cmd_models() {
    api_request "GET" "/models" "" "true"
}

# Get account info
cmd_me() {
    api_request "GET" "/me" "" "true"
}

# Verify repository access
# shellcheck disable=SC2317
cmd_verify() {
    local repo="$1"

    if [[ -z "$repo" ]]; then
        error "Repository required (owner/repo)" "$E_INVALID_ARGS"
    fi

    repo=$(sanitize_repo "$repo")

    # Try to list agents filtered by repo (this will fail if no access)
    # Since API doesn't have direct repo verify, we check via me endpoint
    # which returns accessible repos
    local response
    response=$(api_request "GET" "/me" "" "true")

    # Check if repo is in the accessible repos list
    if echo "$response" | jq -e ".accessibleRepos | contains([\"$repo\"])" >/dev/null 2>&1; then
        echo "{\"accessible\": true, \"repo\": \"$repo\"}"
    elif echo "$response" | jq -e ".accessibleRepos" >/dev/null 2>&1; then
        # Repo not in list
        echo "{\"accessible\": false, \"repo\": \"$repo\"}"
        exit "$E_REPO_INACCESSIBLE"
    else
        # API might not return accessibleRepos, assume accessible
        echo "{\"accessible\": true, \"repo\": \"$repo\", \"note\": \"Unable to verify, assuming accessible\"}"
    fi
}

# Get usage information
cmd_usage() {
    local response
    response=$(api_request "GET" "/me" "" "true")

    # Extract usage information if available
    echo "$response" | jq '{
        account: {email: .email, username: .username},
        subscription: {tier: .tier, status: .subscriptionStatus},
        usage: {
            agentsUsed: (.agentsUsed // 0),
            agentsLimit: (.agentsLimit // "unlimited"),
            computeUsed: (.computeUsed // 0),
            computeLimit: (.computeLimit // "unlimited")
        },
        limits: {
            concurrentAgents: (.concurrentAgentLimit // "unknown"),
            requestsPerMinute: (.rateLimit // "unknown")
        }
    }'
}

#######################################
# Main
#######################################

# Show usage
usage() {
    cat << 'EOF'
Usage: cursor-api.sh [options] <command> [args]

Note: Global options (--verbose, --no-cache) must come BEFORE the command.

Options:
  --no-cache    Disable response caching (must come before command)
  --verbose     Enable verbose output (must come before command)
  --help        Show this help

Commands:
  list [options]                List all agents
    --limit N                   Maximum number of agents to return
    --offset N                  Offset for pagination
  launch [options]              Launch a new agent
    --repo owner/repo           Target repository (required)
    --prompt "..."              Initial prompt (required)
    --model "model-name"        Model to use (optional)
    --branch "branch-name"      Branch name (optional)
    --no-pr                     Don't auto-create PR
  status <agent-id>             Get agent status
  conversation <agent-id>       Get agent conversation
  followup <agent-id> [options] Send follow-up
    --prompt "..."              Message to send (required)
  stop <agent-id>               Stop an agent
  delete <agent-id>             Delete an agent
  models                        List available models
  me                            Get account information
  verify <owner/repo>           Verify repository access
  usage                         Get usage/cost information
  clear-cache                   Clear response cache

Environment:
  CURSOR_API_KEY     Required. Your Cursor API key
  CURSOR_API_BASE    Optional. API base URL override (default: https://api.cursor.com/v0)
  CURSOR_CACHE_TTL   Optional. Cache TTL in seconds (default: 60)

Exit codes:
  0  Success
  1  API error
  2  Authentication missing
  3  Rate limited
  4  Repository not accessible
  5  Invalid arguments
EOF
}

# Main entry point
main() {
    local command=""

    # Parse global options
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --no-cache)
                USE_CACHE=false
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            -*)
                error "Unknown option: $1" "$E_INVALID_ARGS"
                ;;
            *)
                command="$1"
                shift
                break
                ;;
        esac
    done

    if [[ -z "$command" ]]; then
        usage
        exit "$E_INVALID_ARGS"
    fi

    # Execute command
    case "$command" in
        list)
            cmd_list "$@"
            ;;
        launch)
            cmd_launch "$@"
            ;;
        status)
            if [[ $# -eq 0 ]]; then
                error "Agent ID required" "$E_INVALID_ARGS"
            fi
            cmd_status "$1"
            ;;
        conversation)
            if [[ $# -eq 0 ]]; then
                error "Agent ID required" "$E_INVALID_ARGS"
            fi
            cmd_conversation "$1"
            ;;
        followup)
            if [[ $# -eq 0 ]]; then
                error "Agent ID required" "$E_INVALID_ARGS"
            fi
            cmd_followup "$@"
            ;;
        stop)
            if [[ $# -eq 0 ]]; then
                error "Agent ID required" "$E_INVALID_ARGS"
            fi
            cmd_stop "$1"
            ;;
        delete)
            if [[ $# -eq 0 ]]; then
                error "Agent ID required" "$E_INVALID_ARGS"
            fi
            cmd_delete "$1"
            ;;
        models)
            cmd_models
            ;;
        me)
            cmd_me
            ;;
        verify)
            if [[ $# -eq 0 ]]; then
                error "Repository required (owner/repo)" "$E_INVALID_ARGS"
            fi
            cmd_verify "$1"
            ;;
        usage)
            cmd_usage
            ;;
        clear-cache)
            clear_cache
            ;;
        *)
            error "Unknown command: $command" "$E_INVALID_ARGS"
            ;;
    esac
}

main "$@"
