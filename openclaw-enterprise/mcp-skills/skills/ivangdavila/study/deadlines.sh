#!/usr/bin/env bash
# List upcoming deadlines
set -euo pipefail

WORKSPACE="${1:?Usage: deadlines.sh <workspace> [days]}"
DAYS="${2:-30}"

echo "📅 Upcoming Deadlines (next $DAYS days)"
echo ""

NOW_TS=$(date +%s)
FUTURE_TS=$((NOW_TS + DAYS * 86400))

# Combine exam dates and other deadlines
{
  # Exams from subjects
  jq -r '.subjects[] | "\(.exam_date)|\(.name)|exam"' "$WORKSPACE/config.json" 2>/dev/null
  
  # Other deadlines
  jq -r '.deadlines[] | "\(.date)|\(.subject)|\(.type)"' "$WORKSPACE/schedule.json" 2>/dev/null
} | sort -t'|' -k1 | while IFS='|' read -r date name type; do
  [[ -z "$date" ]] && continue
  
  if [[ "$(uname)" == "Darwin" ]]; then
    DATE_TS=$(date -j -f "%Y-%m-%d" "$date" +%s 2>/dev/null || continue)
  else
    DATE_TS=$(date -d "$date" +%s 2>/dev/null || continue)
  fi
  
  # Skip if past or too far future
  [[ $DATE_TS -lt $NOW_TS || $DATE_TS -gt $FUTURE_TS ]] && continue
  
  DAYS_LEFT=$(( (DATE_TS - NOW_TS) / 86400 ))
  
  if [[ $DAYS_LEFT -eq 0 ]]; then
    ICON="🔴 TODAY"
  elif [[ $DAYS_LEFT -eq 1 ]]; then
    ICON="🔴 Tomorrow"
  elif [[ $DAYS_LEFT -lt 7 ]]; then
    ICON="🟡 $DAYS_LEFT days"
  else
    ICON="🟢 $DAYS_LEFT days"
  fi
  
  TYPE_ICON="📝"
  [[ "$type" == "exam" ]] && TYPE_ICON="📚"
  
  echo "$TYPE_ICON $date: $name ($type) — $ICON"
done

echo ""
echo "---"
echo "Add deadline: Edit $WORKSPACE/schedule.json"
