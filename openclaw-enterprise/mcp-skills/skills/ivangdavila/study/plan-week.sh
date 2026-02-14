#!/usr/bin/env bash
# Generate weekly study schedule
set -euo pipefail

WORKSPACE="${1:?Usage: plan-week.sh <workspace>}"

echo "📅 Weekly Study Plan"
echo ""

# Get subjects and their weekly hours
SUBJECTS=$(jq -r '.subjects[] | "\(.name)|\(.weekly_hours)|\(.exam_date)"' "$WORKSPACE/config.json")

if [[ -z "$SUBJECTS" ]]; then
  echo "No subjects configured. Add subjects first:"
  echo "  ./scripts/add-subject.sh $WORKSPACE \"Subject\" \"2025-06-15\" 5"
  exit 1
fi

TOTAL_HOURS=0

echo "Subjects:"
echo "$SUBJECTS" | while IFS='|' read -r name hours exam; do
  DAYS_TO_EXAM=$(( ($(date -d "$exam" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$exam" +%s) - $(date +%s)) / 86400 ))
  echo "  📖 $name: $hours hrs/week (exam in $DAYS_TO_EXAM days)"
  TOTAL_HOURS=$((TOTAL_HOURS + hours))
done

echo ""
echo "---"
echo ""
echo "Suggested weekly distribution:"
echo ""

# Simple distribution across days
DAYS=("Monday" "Tuesday" "Wednesday" "Thursday" "Friday" "Saturday" "Sunday")

jq -r '.subjects[] | "\(.id)|\(.name)|\(.weekly_hours)"' "$WORKSPACE/config.json" | while IFS='|' read -r id name hours; do
  SESSIONS=$((hours * 2))  # 30-min sessions
  echo "📚 $name ($hours hours = $SESSIONS × 30min sessions)"
  
  for ((i=0; i<SESSIONS && i<7; i++)); do
    echo "   ${DAYS[$i]}: 30min"
  done
  echo ""
done

echo "---"
echo ""
echo "💡 Tips:"
echo "   - Schedule hardest subjects during peak energy (morning?)"
echo "   - Space subjects across days, don't block-study"
echo "   - Leave 20% buffer for unexpected"
echo ""
echo "Start a session: ./scripts/session.sh $WORKSPACE <subject-id>"
