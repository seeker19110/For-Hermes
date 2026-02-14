#!/usr/bin/env bash
# Show study progress by subject
set -euo pipefail

WORKSPACE="${1:?Usage: progress.sh <workspace>}"

echo "📊 Study Progress"
echo ""

NOW_TS=$(date +%s)

jq -r '.subjects[] | "\(.id)|\(.name)|\(.exam_date)|\(.weekly_hours)|\(.type)"' "$WORKSPACE/config.json" | while IFS='|' read -r id name exam hours type; do
  # Calculate days until exam
  if [[ "$(uname)" == "Darwin" ]]; then
    EXAM_TS=$(date -j -f "%Y-%m-%d" "$exam" +%s 2>/dev/null || echo $NOW_TS)
  else
    EXAM_TS=$(date -d "$exam" +%s 2>/dev/null || echo $NOW_TS)
  fi
  DAYS_LEFT=$(( (EXAM_TS - NOW_TS) / 86400 ))
  
  # Count sessions
  SESSION_COUNT=$(find "$WORKSPACE/sessions" -name "*.json" -exec grep -l "\"subject\": \"$id\"" {} \; 2>/dev/null | wc -l | tr -d ' ')
  
  # Calculate total study time from sessions
  TOTAL_MINS=$(find "$WORKSPACE/sessions" -name "*.json" -exec grep -l "\"subject\": \"$id\"" {} \; 2>/dev/null | xargs -I{} jq -r '.actual_minutes // 0' {} 2>/dev/null | awk '{s+=$1} END {print s+0}')
  TOTAL_HOURS=$(echo "scale=1; $TOTAL_MINS / 60" | bc)
  
  if [[ $DAYS_LEFT -lt 0 ]]; then
    STATUS="✅ Exam passed"
  elif [[ $DAYS_LEFT -lt 7 ]]; then
    STATUS="🔴 $DAYS_LEFT days"
  elif [[ $DAYS_LEFT -lt 14 ]]; then
    STATUS="🟡 $DAYS_LEFT days"
  else
    STATUS="🟢 $DAYS_LEFT days"
  fi
  
  echo "📖 $name ($type)"
  echo "   Exam: $exam ($STATUS)"
  echo "   Sessions: $SESSION_COUNT (${TOTAL_HOURS}h total)"
  echo "   Target: ${hours}h/week"
  echo ""
done

echo "---"
echo "Start session: ./scripts/session.sh $WORKSPACE <subject-id>"
echo "View deadlines: ./scripts/deadlines.sh $WORKSPACE"
