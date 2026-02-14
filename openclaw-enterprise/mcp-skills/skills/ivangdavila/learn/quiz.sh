#!/usr/bin/env bash
# Generate verification quiz for a topic
set -euo pipefail

WORKSPACE="${1:?Usage: quiz.sh <workspace> <topic-id> [num-questions]}"
TOPIC_ID="${2:?Provide topic ID}"
NUM="${3:-5}"

QUIZ_ID="quiz-$(date +%Y%m%d-%H%M%S)"
QUIZ_FILE="$WORKSPACE/quizzes/$QUIZ_ID.md"

mkdir -p "$WORKSPACE/quizzes"

TOPIC_NAME=$(jq -r --arg id "$TOPIC_ID" '.topics[] | select(.id == $id) | .name' "$WORKSPACE/index.json")

cat > "$QUIZ_FILE" << EOF
# Verification Quiz: $TOPIC_NAME

**Date:** $(date -Iseconds)
**Topic:** $TOPIC_ID
**Questions:** $NUM

---

## Instructions
1. Answer each question WITHOUT looking at notes
2. Rate confidence (1-5) BEFORE checking answer
3. Check answer, note if correct
4. Track calibration: confidence vs actual

---

## Questions

EOF

# Pull random concepts from topic
jq -r --arg topic "$TOPIC_ID" \
  '[.concepts[] | select(.topic == $topic)] | .[:'"$NUM"'] | .[] | "### Q: \(.question)\n\n**Your answer:**\n\n**Confidence (1-5):**\n\n**Correct answer:** \(.answer)\n\n**Result:** ✅/❌\n\n---\n"' \
  "$WORKSPACE/concepts.json" >> "$QUIZ_FILE" || true

cat >> "$QUIZ_FILE" << 'EOF'

## Summary

- **Correct:** /
- **Calibration:** (avg confidence of correct - avg confidence of wrong)
- **Focus areas:**

## Next Steps
- [ ] Review missed concepts
- [ ] Add new concepts discovered
- [ ] Schedule re-quiz in 1 week
EOF

echo "✅ Quiz generated: $QUIZ_FILE"
echo ""
echo "Open the file, answer questions, then check your calibration."
