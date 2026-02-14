#!/usr/bin/env bash
# Add a subject with exam date and weekly hours
set -euo pipefail

WORKSPACE="${1:?Usage: add-subject.sh <workspace> <name> <exam-date> <weekly-hours> [type]}"
NAME="${2:?Provide subject name}"
EXAM_DATE="${3:?Provide exam date (YYYY-MM-DD)}"
WEEKLY_HOURS="${4:?Provide weekly hours}"
TYPE="${5:-conceptual}"  # memorization|conceptual|problem-solving|writing|practical

SUBJECT_ID="$(echo "$NAME" | tr '[:upper:] ' '[:lower:]-')"
SUBJECT_DIR="$WORKSPACE/subjects/$SUBJECT_ID"

mkdir -p "$SUBJECT_DIR"

# Create subject config
cat > "$SUBJECT_DIR/config.json" << EOF
{
  "id": "$SUBJECT_ID",
  "name": "$NAME",
  "type": "$TYPE",
  "exam_date": "$EXAM_DATE",
  "weekly_hours": $WEEKLY_HOURS,
  "created": "$(date -Iseconds)",
  "topics": [],
  "completed_hours": 0
}
EOF

# Create materials template
cat > "$SUBJECT_DIR/syllabus.md" << 'EOF'
# Syllabus

## Topics
1. 
2. 
3. 

## Key Dates
- 

## Resources
- Textbook: 
- Lecture notes: 
- Practice problems: 
EOF

# Add to main config
jq --arg id "$SUBJECT_ID" --arg name "$NAME" --arg exam "$EXAM_DATE" --argjson hours "$WEEKLY_HOURS" --arg type "$TYPE" \
  '.subjects += [{"id": $id, "name": $name, "exam_date": $exam, "weekly_hours": $hours, "type": $type}]' \
  "$WORKSPACE/config.json" > "$WORKSPACE/config.json.tmp" && \
  mv "$WORKSPACE/config.json.tmp" "$WORKSPACE/config.json"

# Add exam deadline
jq --arg name "$NAME" --arg date "$EXAM_DATE" \
  '.deadlines += [{"subject": $name, "type": "exam", "date": $date}]' \
  "$WORKSPACE/schedule.json" > "$WORKSPACE/schedule.json.tmp" && \
  mv "$WORKSPACE/schedule.json.tmp" "$WORKSPACE/schedule.json"

echo "✅ Added subject: $NAME"
echo "   Type: $TYPE"
echo "   Exam: $EXAM_DATE"
echo "   Weekly hours: $WEEKLY_HOURS"
echo ""
echo "Edit syllabus: $SUBJECT_DIR/syllabus.md"
