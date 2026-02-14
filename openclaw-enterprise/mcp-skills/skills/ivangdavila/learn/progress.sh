#!/usr/bin/env bash
# Show mastery progress by topic
set -euo pipefail

WORKSPACE="${1:?Usage: progress.sh <workspace> [topic-id]}"
TOPIC_ID="${2:-}"

echo "📊 Learning Progress"
echo ""

if [[ -n "$TOPIC_ID" ]]; then
  # Show specific topic
  TOPIC=$(jq -r --arg id "$TOPIC_ID" '.topics[] | select(.id == $id)' "$WORKSPACE/index.json")
  NAME=$(echo "$TOPIC" | jq -r '.name')
  
  CONCEPTS=$(jq --arg topic "$TOPIC_ID" '[.concepts[] | select(.topic == $topic)]' "$WORKSPACE/concepts.json")
  TOTAL=$(echo "$CONCEPTS" | jq 'length')
  
  echo "📖 $NAME"
  echo "   Concepts: $TOTAL"
  echo ""
  echo "   Concepts:"
  echo "$CONCEPTS" | jq -r '.[] | "   - \(.name) (interval: \(.interval)d, next: \(.next_review))"'
else
  # Show all topics
  jq -r '.topics[] | "📖 [\(.id)] \(.name)"' "$WORKSPACE/index.json"
  echo ""
  
  TOTAL_CONCEPTS=$(jq '.concepts | length' "$WORKSPACE/concepts.json")
  TODAY=$(date +%Y-%m-%d)
  DUE=$(jq -r --arg today "$TODAY" '[.concepts[] | select(.next_review <= $today)] | length' "$WORKSPACE/concepts.json")
  
  echo "---"
  echo "Total concepts: $TOTAL_CONCEPTS"
  echo "Due for review: $DUE"
  echo ""
  echo "Details: ./scripts/progress.sh $WORKSPACE <topic-id>"
fi
