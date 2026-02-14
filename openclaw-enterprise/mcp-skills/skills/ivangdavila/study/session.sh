#!/usr/bin/env bash
# Start a timed study session
set -euo pipefail

WORKSPACE="${1:?Usage: session.sh <workspace> <subject-id> [duration-min]}"
SUBJECT_ID="${2:?Provide subject ID}"
DURATION="${3:-25}"  # Pomodoro default

SESSION_ID="session-$(date +%Y%m%d-%H%M%S)"
SESSION_FILE="$WORKSPACE/sessions/$SESSION_ID.json"

mkdir -p "$WORKSPACE/sessions"

SUBJECT_NAME=$(jq -r --arg id "$SUBJECT_ID" '.subjects[] | select(.id == $id) | .name' "$WORKSPACE/config.json")
SUBJECT_TYPE=$(jq -r --arg id "$SUBJECT_ID" '.subjects[] | select(.id == $id) | .type' "$WORKSPACE/config.json")

if [[ -z "$SUBJECT_NAME" || "$SUBJECT_NAME" == "null" ]]; then
  echo "❌ Subject not found: $SUBJECT_ID"
  exit 1
fi

echo "📚 Starting study session"
echo "   Subject: $SUBJECT_NAME ($SUBJECT_TYPE)"
echo "   Duration: $DURATION minutes"
echo ""
echo "---"
echo "📝 Before you start:"
echo "   1. What will you focus on? (specific topic)"
echo "   2. What's your goal for this session?"
echo ""

read -p "Topic: " TOPIC
read -p "Goal: " GOAL

echo ""
echo "⏱️  Session started at $(date +%H:%M)"
echo "    Timer: $DURATION minutes"
echo ""
echo "Press Enter when done (or Ctrl+C to cancel)..."

START_TIME=$(date +%s)
read

END_TIME=$(date +%s)
ACTUAL_MINUTES=$(( (END_TIME - START_TIME) / 60 ))

echo ""
echo "📝 Session review:"
read -p "What did you accomplish? " ACCOMPLISHMENT
read -p "Difficulty (1-5): " DIFFICULTY
read -p "Key concepts to review later: " REVIEW_NOTES

# Log session
cat > "$SESSION_FILE" << EOF
{
  "id": "$SESSION_ID",
  "subject": "$SUBJECT_ID",
  "subject_name": "$SUBJECT_NAME",
  "topic": "$TOPIC",
  "goal": "$GOAL",
  "accomplishment": "$ACCOMPLISHMENT",
  "difficulty": $DIFFICULTY,
  "review_notes": "$REVIEW_NOTES",
  "planned_minutes": $DURATION,
  "actual_minutes": $ACTUAL_MINUTES,
  "timestamp": "$(date -Iseconds)"
}
EOF

# Update subject hours
CURRENT_HOURS=$(jq -r --arg id "$SUBJECT_ID" '.subjects[] | select(.id == $id) | .completed_hours // 0' "$WORKSPACE/config.json")
NEW_HOURS=$(echo "$CURRENT_HOURS + $ACTUAL_MINUTES / 60" | bc -l)

# Update would require more complex jq...

echo ""
echo "✅ Session logged: $SESSION_FILE"
echo "   Duration: $ACTUAL_MINUTES minutes"
echo ""
echo "🎯 Remember: Review '$REVIEW_NOTES' tomorrow!"
