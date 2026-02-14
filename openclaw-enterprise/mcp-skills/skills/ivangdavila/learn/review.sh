#!/usr/bin/env bash
# Run due reviews with active recall (SM-2 algorithm)
set -euo pipefail

WORKSPACE="${1:?Usage: review.sh <workspace>}"

TODAY=$(date +%Y-%m-%d)

# Find due concepts
DUE=$(jq -r --arg today "$TODAY" \
  '[.concepts[] | select(.next_review <= $today)] | length' \
  "$WORKSPACE/concepts.json")

if [[ "$DUE" -eq 0 ]]; then
  echo "✅ No reviews due today!"
  echo "   Run ./scripts/schedule.sh $WORKSPACE to see upcoming"
  exit 0
fi

echo "📚 $DUE concept(s) due for review"
echo ""
echo "For each concept, you'll be asked the question."
echo "After answering (in your head or aloud), rate yourself:"
echo "  0 = Complete blackout"
echo "  1 = Wrong, but recognized answer"
echo "  2 = Wrong, but answer felt familiar"
echo "  3 = Correct with serious difficulty"
echo "  4 = Correct with some hesitation"
echo "  5 = Perfect recall"
echo ""
echo "---"
echo ""

# Process each due concept
jq -c --arg today "$TODAY" \
  '.concepts[] | select(.next_review <= $today)' \
  "$WORKSPACE/concepts.json" | while read -r concept; do
  
  ID=$(echo "$concept" | jq -r '.id')
  NAME=$(echo "$concept" | jq -r '.name')
  QUESTION=$(echo "$concept" | jq -r '.question')
  ANSWER=$(echo "$concept" | jq -r '.answer')
  
  echo "📖 Concept: $NAME"
  echo "❓ Question: $QUESTION"
  echo ""
  read -p "Press Enter when ready to see answer..."
  echo ""
  echo "✅ Answer: $ANSWER"
  echo ""
  read -p "Rate (0-5): " RATING
  
  # Log review (actual SM-2 calculation would happen here)
  TIMESTAMP=$(date -Iseconds)
  REVIEW_FILE="$WORKSPACE/reviews/review-$(date +%Y%m%d-%H%M%S).json"
  mkdir -p "$WORKSPACE/reviews"
  
  cat > "$REVIEW_FILE" << EOF
{
  "concept_id": "$ID",
  "concept_name": "$NAME",
  "rating": $RATING,
  "timestamp": "$TIMESTAMP"
}
EOF

  echo "📝 Review logged: $REVIEW_FILE"
  echo "---"
  echo ""
done

echo "✅ Review session complete!"
