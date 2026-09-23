# UI/UX Deep Review Checklist

Load only when a task needs a broad audit or implementation review.

## 1. Context and system fit

- Project-local UI rules/source of truth identified.
- Existing token/theme/component/icon/typography system identified.
- Similar page/component patterns inspected.
- No new dependency/design primitive without a demonstrated gap.
- Visual direction matches product/job, not a generic trend.

## 2. Hierarchy and content

- One clear primary task/action per context.
- Heading order and grouping reflect information structure.
- Long-form content has readable measure and line-height.
- Labels/CTA/error copy are specific and action-oriented.
- Decorative containers do not create unnecessary card-within-card depth.

## 3. States and recovery

- Loading/pending state is proportionate and does not cause avoidable layout shift.
- Empty state explains next action when useful.
- Error state includes recovery.
- Offline/queued/stale/conflict states considered when relevant.
- Success is not claimed before authoritative state confirms it.
- Destructive actions have appropriate friction.

## 4. Accessibility

- Semantic element first; ARIA only where semantics need extension.
- Every interactive element has an accessible name.
- Visible focus and logical keyboard order.
- Modal/popover focus behavior is correct.
- Dynamic updates use live regions only where meaningful.
- No color-only status.
- Contrast meets project policy.
- Reduced motion preserves meaning.
- Zoom/reflow does not lose content or controls.

## 5. Forms

- Labels are persistent.
- Input type/inputMode/autocomplete are appropriate.
- Validation timing is not hostile.
- Error is associated with field; multi-error flows consider summary/focus.
- Disabled/read-only/loading states are distinguishable.
- Error text space/layout shift is handled.
- Unsaved data behavior is explicit where loss is plausible.

## 6. Responsive and input modes

- Mobile layout reprioritizes rather than merely shrinks.
- No unintended horizontal overflow.
- Touch targets are usable.
- Hover-only interactions have touch/keyboard equivalents.
- Dense tables preserve comparison or provide an intentional alternative.
- Virtual keyboard does not hide critical action/input on mobile.

## 7. Motion and performance

- Every animation has a purpose.
- Animation is interruptible and non-blocking.
- Prefer compositor-friendly properties.
- No `transition-all` by default.
- Skeleton dimensions approximate final content.
- Heavy effects/blur/video/canvas are justified by product value.
- Large datasets/media have pagination, virtualization, lazy loading or aggregation when needed.

## 8. Tables and charts

- Table headers/sort/filter state are understandable.
- Numeric alignment supports scanning.
- Chart title, unit, range and legend are clear.
- Exact values are available where decisions require them.
- Chart information has an accessible textual/table representation when needed.
- Avoid 3D, misleading axes and unnecessary dual-axis complexity.

## 9. Verification

Use repository-defined commands. Typical evidence may include:
- formatter/lint/typecheck/build;
- unit/component tests;
- Playwright/Cypress;
- axe/accessibility checks;
- screenshots at relevant breakpoints/themes;
- keyboard-only walkthrough;
- assistive-tech check for high-risk interaction;
- performance/bundle check for heavy UI changes.

Report what actually ran and what did not.
