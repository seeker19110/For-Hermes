#!/usr/bin/env bash
# Create new learning topic
set -euo pipefail

WORKSPACE="${1:?Usage: new-topic.sh <workspace> <topic-name> [goal]}"
TOPIC="${2:?Provide topic name}"
GOAL="${3:-Learn and understand $TOPIC}"

# Generate ID
TOPIC_ID="$(echo "$TOPIC" | tr '[:upper:] ' '[:lower:]-')-$(date +%Y%m%d)"
TOPIC_DIR="$WORKSPACE/topics/$TOPIC_ID"

mkdir -p "$TOPIC_DIR"

# Create metadata
cat > "$TOPIC_DIR/meta.json" << EOF
{
  "id": "$TOPIC_ID",
  "name": "$TOPIC",
  "goal": "$GOAL",
  "created": "$(date -Iseconds)",
  "status": "active",
  "concepts": [],
  "mastery": 0
}
EOF

# Create curriculum template
cat > "$TOPIC_DIR/curriculum.md" << 'EOF'
# Learning Plan

## Goal
<!-- What do you want to be able to DO after learning this? -->

## Prerequisites
<!-- What do you need to know first? -->

## Concepts to Master
1. 
2. 
3. 

## Resources
- 

## Milestones
- [ ] Understand basics
- [ ] Apply to simple problem
- [ ] Teach to someone else
EOF

# Create notes file
touch "$TOPIC_DIR/notes.md"

# Update index
jq --arg id "$TOPIC_ID" --arg name "$TOPIC" \
  '.topics += [{"id": $id, "name": $name, "created": now | todate}]' \
  "$WORKSPACE/index.json" > "$WORKSPACE/index.json.tmp" && \
  mv "$WORKSPACE/index.json.tmp" "$WORKSPACE/index.json"

echo "✅ Created topic: $TOPIC_ID"
echo "   $TOPIC_DIR/curriculum.md — define learning plan"
echo "   $TOPIC_DIR/notes.md       — study notes"
echo ""
echo "Add concepts: ./scripts/add-concept.sh $WORKSPACE $TOPIC_ID \"concept name\""
