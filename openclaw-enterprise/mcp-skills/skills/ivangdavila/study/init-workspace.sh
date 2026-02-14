#!/usr/bin/env bash
# Initialize study workspace
set -euo pipefail

WORKSPACE="${1:?Usage: init-workspace.sh <path>}"

mkdir -p "$WORKSPACE"/{subjects,sessions,exams,materials}

cat > "$WORKSPACE/config.json" << 'EOF'
{
  "level": "undergraduate",
  "technique": "pomodoro",
  "created": "'"$(date -Iseconds)"'",
  "subjects": []
}
EOF

cat > "$WORKSPACE/schedule.json" << 'EOF'
{
  "weekly_hours": {},
  "deadlines": []
}
EOF

echo "✅ Study workspace initialized at $WORKSPACE"
echo "   - subjects/  : subject folders"
echo "   - sessions/  : study session logs"
echo "   - exams/     : exam prep materials"
echo "   - materials/ : notes, summaries, flashcards"
echo ""
echo "Add subject: ./scripts/add-subject.sh $WORKSPACE \"Subject Name\" \"2025-06-15\" 5"
