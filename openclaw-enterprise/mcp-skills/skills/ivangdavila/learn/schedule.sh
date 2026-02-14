#!/usr/bin/env bash
# Show upcoming review schedule
set -euo pipefail

WORKSPACE="${1:?Usage: schedule.sh <workspace> [days]}"
DAYS="${2:-7}"

echo "📅 Review Schedule (next $DAYS days)"
echo ""

TODAY=$(date +%Y-%m-%d)

for i in $(seq 0 $DAYS); do
  if [[ "$(uname)" == "Darwin" ]]; then
    DAY=$(date -v+"$i"d +%Y-%m-%d)
  else
    DAY=$(date -d "+$i day" +%Y-%m-%d)
  fi
  
  COUNT=$(jq -r --arg day "$DAY" '[.concepts[] | select(.next_review == $day)] | length' "$WORKSPACE/concepts.json")
  
  if [[ "$DAY" == "$TODAY" ]]; then
    LABEL="(today)"
  else
    LABEL=""
  fi
  
  if [[ "$COUNT" -gt 0 ]]; then
    echo "  $DAY: $COUNT concept(s) $LABEL"
  fi
done

echo ""
echo "Run reviews: ./scripts/review.sh $WORKSPACE"
