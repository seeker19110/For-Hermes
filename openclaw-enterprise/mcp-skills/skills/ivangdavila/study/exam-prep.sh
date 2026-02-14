#!/usr/bin/env bash
# Create exam preparation plan
set -euo pipefail

WORKSPACE="${1:?Usage: exam-prep.sh <workspace> <subject-id>}"
SUBJECT_ID="${2:?Provide subject ID}"

SUBJECT=$(jq -r --arg id "$SUBJECT_ID" '.subjects[] | select(.id == $id)' "$WORKSPACE/config.json")
NAME=$(echo "$SUBJECT" | jq -r '.name')
EXAM_DATE=$(echo "$SUBJECT" | jq -r '.exam_date')
TYPE=$(echo "$SUBJECT" | jq -r '.type')

if [[ -z "$NAME" || "$NAME" == "null" ]]; then
  echo "❌ Subject not found: $SUBJECT_ID"
  exit 1
fi

# Calculate days until exam
if [[ "$(uname)" == "Darwin" ]]; then
  EXAM_TS=$(date -j -f "%Y-%m-%d" "$EXAM_DATE" +%s)
else
  EXAM_TS=$(date -d "$EXAM_DATE" +%s)
fi
NOW_TS=$(date +%s)
DAYS_LEFT=$(( (EXAM_TS - NOW_TS) / 86400 ))

PREP_FILE="$WORKSPACE/exams/prep-$SUBJECT_ID-$(date +%Y%m%d).md"
mkdir -p "$WORKSPACE/exams"

cat > "$PREP_FILE" << EOF
# Exam Prep: $NAME

**Exam Date:** $EXAM_DATE ($DAYS_LEFT days remaining)
**Subject Type:** $TYPE
**Created:** $(date -Iseconds)

---

## Timeline

EOF

if [[ $DAYS_LEFT -gt 14 ]]; then
  cat >> "$PREP_FILE" << 'EOF'
### Phase 1: Content Review (Now → 2 weeks before)
- [ ] Review all topics from syllabus
- [ ] Fill knowledge gaps
- [ ] Create summary notes

### Phase 2: Active Practice (2 weeks → 1 week before)
- [ ] Practice problems / past papers
- [ ] Identify weak areas
- [ ] Focus study on weaknesses

### Phase 3: Exam Simulation (1 week → exam)
- [ ] Full practice tests under timed conditions
- [ ] Review mistakes deeply
- [ ] Light review only last 2 days
EOF
elif [[ $DAYS_LEFT -gt 7 ]]; then
  cat >> "$PREP_FILE" << 'EOF'
### Phase 1: Rapid Review (Now → 3 days before)
- [ ] Review main concepts
- [ ] Practice key problem types

### Phase 2: Testing (3 days → exam)
- [ ] Practice tests
- [ ] Review mistakes
- [ ] Sleep well night before
EOF
else
  cat >> "$PREP_FILE" << 'EOF'
### Emergency Mode: Focus on High-Yield
- [ ] Identify most likely exam topics
- [ ] Practice those specifically
- [ ] Don't try to learn new material
- [ ] Get sleep — it consolidates memory
EOF
fi

cat >> "$PREP_FILE" << EOF

---

## Topics to Review

<!-- List from syllabus, mark confidence level -->

| Topic | Confidence (1-5) | Priority |
|-------|-----------------|----------|
| | | |

---

## Past Papers / Practice Tests

| Date | Score | Weak Areas |
|------|-------|------------|
| | | |

---

## Day-Before Checklist

- [ ] Light review only (no cramming)
- [ ] Prepare materials (pens, ID, etc.)
- [ ] Know exam location and time
- [ ] Set multiple alarms
- [ ] Sleep 7-8 hours

## Day-Of Checklist

- [ ] Eat protein + complex carbs
- [ ] Arrive 15 min early
- [ ] Quick confidence review (no new material)
- [ ] Bathroom before start
EOF

echo "✅ Exam prep plan created: $PREP_FILE"
echo ""
echo "📊 Status:"
echo "   Subject: $NAME"
echo "   Days until exam: $DAYS_LEFT"
echo "   Type: $TYPE"
