#!/usr/bin/env bash
# Initialize learning workspace
set -euo pipefail

WORKSPACE="${1:?Usage: init-workspace.sh <path>}"

mkdir -p "$WORKSPACE"/{topics,reviews,quizzes,notes}

cat > "$WORKSPACE/config.json" << 'EOF'
{
  "depth": "standard",
  "learner_type": "curiosity",
  "spaced_review": true,
  "created": "'"$(date -Iseconds)"'"
}
EOF

cat > "$WORKSPACE/concepts.json" << 'EOF'
{
  "concepts": []
}
EOF

cat > "$WORKSPACE/index.json" << 'EOF'
{
  "topics": []
}
EOF

echo "✅ Learning workspace initialized at $WORKSPACE"
echo "   - topics/    : learning topics"
echo "   - reviews/   : review logs"
echo "   - quizzes/   : verification quizzes"
echo "   - notes/     : study notes"
