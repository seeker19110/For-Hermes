#!/usr/bin/env bash
# Add concept to spaced repetition system
set -euo pipefail

WORKSPACE="${1:?Usage: add-concept.sh <workspace> <topic-id> <concept> [question] [answer]}"
TOPIC_ID="${2:?Provide topic ID}"
CONCEPT="${3:?Provide concept name}"
QUESTION="${4:-What is $CONCEPT?}"
ANSWER="${5:-}"

CONCEPT_ID="$(date +%Y%m%d%H%M%S)-$(echo "$CONCEPT" | tr '[:upper:] ' '[:lower:]-' | head -c 20)"

# Initial interval: 1 day, easiness factor 2.5 (SM-2 algorithm)
NEXT_REVIEW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)

# Add to concepts database
jq --arg id "$CONCEPT_ID" \
   --arg topic "$TOPIC_ID" \
   --arg name "$CONCEPT" \
   --arg q "$QUESTION" \
   --arg a "$ANSWER" \
   --arg next "$NEXT_REVIEW" \
   '.concepts += [{
     "id": $id,
     "topic": $topic,
     "name": $name,
     "question": $q,
     "answer": $a,
     "interval": 1,
     "easiness": 2.5,
     "repetitions": 0,
     "next_review": $next,
     "created": now | todate,
     "history": []
   }]' "$WORKSPACE/concepts.json" > "$WORKSPACE/concepts.json.tmp" && \
   mv "$WORKSPACE/concepts.json.tmp" "$WORKSPACE/concepts.json"

echo "✅ Added concept: $CONCEPT"
echo "   Question: $QUESTION"
echo "   Next review: $NEXT_REVIEW"
echo ""
echo "Run reviews: ./scripts/review.sh $WORKSPACE"
