---
name: ui-ux
description: "Thiết kế, triển khai và audit UI/UX cho mọi frontend project theo context, design system hiện hữu, accessibility và verification."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ui, ux, frontend, accessibility, design-system, forms, charts, responsive, motion]
    related_skills: [project-harness-engineering]
---

# UI/UX — Generic Agent Skill

Skill này giúp Hermes thiết kế, triển khai và audit giao diện **trên bất kỳ repository frontend nào**.
Nó không mang design system riêng của một project và không được ghi đè convention/token/component
library đang tồn tại trong project đích.

## When to Use

Dùng khi người dùng yêu cầu:
- thiết kế/redesign page, component, form, dashboard, table, chart, modal, navigation;
- review/audit UI/UX, accessibility, responsive, motion, visual hierarchy;
- chuyển mockup/spec thành implementation;
- cải thiện trải nghiệm mobile/desktop, loading/error/empty states;
- xây hoặc chuẩn hóa design-system workflow.

Không dùng skill này để tự áp một palette, font, icon library, animation library hay visual style
chung lên mọi project.

## Precedence

Khi có xung đột, ưu tiên theo thứ tự:

1. Security, privacy, business/domain correctness.
2. User request và acceptance criteria hiện tại.
3. Project-local instructions: AGENTS.md, CLAUDE.md, .hermes.md, rules, specs, ADR.
4. Existing project design system: tokens, components, theme, content conventions.
5. Existing implementation patterns đã được kiểm chứng trong repo.
6. Skill này.
7. External inspiration/reference.

Nếu project có guideline riêng, **adapt skill này vào project**, không adapt project theo skill.

## Core Workflow

### 1. Inspect trước khi design

Trước khi đề xuất UI, xác minh:
- framework/runtime và package versions;
- styling system (Tailwind/CSS Modules/CSS-in-JS/etc.);
- token/theme source of truth;
- component library + icon system;
- routing/layout conventions;
- accessibility/test tooling;
- responsive breakpoints;
- các màn hình/component gần nhất có thể reuse;
- project rules và verification commands.

Không đoán từ tên repo. Không tạo component/token mới trước khi tìm pattern hiện hữu.

### 2. Xác định context bằng một dominant intent

Viết một intent ngắn 2–5 từ + constraint quan trọng, ví dụ:
- `mobile checkout recovery`
- `desktop analytics comparison`
- `long-form reading focus`
- `voice latency feedback`
- `keyboard form errors`

Sau đó đọc `references/decision-contract.json`, áp `must-have` và các condition match.

Không gom accessibility + motion + color + hierarchy + forms + responsive vào một pass mơ hồ.
Nếu có nhiều outcome độc lập, review tuần tự.

### 3. Chọn posture theo sản phẩm, không theo trend

Xác định:
- persona/job-to-be-done;
- device/input/network constraints;
- information shape: prose, form, realtime, table/chart, workflow, media;
- dominant risk: hiểu sai, mất dữ liệu, thao tác nhầm, overload, latency uncertainty, focus loss;
- density phù hợp;
- motion budget;
- content hierarchy.

“Glass”, “bento”, “3D”, “neon”, “minimal” chỉ là implementation choices, không phải requirement.

### 4. Reuse trước, extend sau

Ưu tiên:
1. reuse component hiện hữu;
2. compose component hiện hữu;
3. extend variant/token hiện hữu;
4. chỉ tạo primitive mới khi có gap thật.

Nếu cần primitive mới, nêu vì sao pattern hiện tại không đủ. Không tạo design system thứ hai.

### 5. Thiết kế state như contract

Với capability có async/input/state, xét:
- initial/empty;
- loading/pending;
- success/data;
- error + recovery;
- validation;
- permission/disabled/read-only;
- offline/queued/retry;
- conflict/stale data;
- destructive confirmation khi cần.

Chỉ áp state có thật. Không bịa fake empty/loading/error state để “đủ checklist”.

### 6. Accessibility là behavior, không phải decoration

Mặc định:
- semantic HTML trước ARIA;
- accessible name rõ;
- label thật cho form control;
- keyboard order/operation đầy đủ;
- visible focus tức thì;
- không dùng color-only meaning;
- reduced-motion;
- status/live-region chỉ khi outcome cần được công bố;
- touch target đủ lớn theo project/standard hiện hành;
- zoom/reflow không làm mất chức năng;
- contrast theo policy của project, tối thiểu WCAG AA nếu project không quy định cao hơn.

Khi screen-reader behavior quan trọng, DOM/axe xanh chưa đủ thay cho assistive-tech verification nếu
project yêu cầu mức bằng chứng đó.

### 7. Responsive = reprioritize, không chỉ shrink

Trên màn nhỏ:
- giữ primary task/action;
- collapse/reorder secondary information;
- table phải giữ khả năng so sánh quan trọng;
- tránh horizontal overflow ngoài vùng có chủ ý;
- interaction không phụ thuộc hover;
- touch/mobile keyboard/autofill được xét riêng.

### 8. Motion có chức năng

Motion hợp lệ khi giải thích:
- quan hệ không gian;
- state transition;
- cause/effect;
- progress;
- focus/attention có chủ ý.

Ưu tiên transform/opacity; tránh animate layout nếu không cần. Không dùng `transition-all` làm mặc
định. Animation phải interruptible, không block task và có reduced-motion behavior.

### 9. Forms

- dùng `type`, `inputMode`, `autocomplete` đúng semantics;
- validation không spam khi người dùng đang gõ nếu không có lý do;
- reserve error space khi layout shift là rủi ro;
- nhiều lỗi: cân nhắc error summary + focus + link tới field;
- read-only khác disabled;
- destructive/irreversible action tách khỏi primary flow;
- unsaved draft/autosave chỉ thêm khi product contract cho phép.

### 10. Data-heavy UI và charts

Ưu tiên scanability hơn decoration:
- numbers cần so sánh dùng tabular figures nếu phù hợp;
- title/unit/time range rõ;
- sort/filter/pagination state rõ;
- chart cần context và text/table alternative khi thông tin quyết định phụ thuộc vào nó;
- đừng dùng pie/donut với quá nhiều category, 3D chart, dual-axis khó diễn giải chỉ vì thẩm mỹ;
- dataset lớn: aggregate/sample + drill-down thay vì render mọi điểm;
- mobile giữ quan hệ dữ liệu quan trọng, không chỉ ẩn cột tùy tiện.

### 11. Content & feedback

- dùng ngôn ngữ của sản phẩm/project;
- CTA là hành động cụ thể;
- error nói điều gì xảy ra + người dùng làm gì tiếp;
- không toast success khi outcome đã nhìn thấy rõ;
- không dùng icon-only nếu meaning không rõ hoặc thiếu accessible name;
- skeleton phải gần kích thước content thật để giảm layout shift.

### 12. Implement nhỏ và verify thật

Vòng lặp:

```text
Inspect → Intent → Constraints → Reuse decision → Implement
→ Static checks → Focused tests → A11y/visual checks
→ Responsive check → Diff review → Evidence
```

Chạy command thật từ project; không bịa `npm run lint`/Playwright nếu repo không có.

## Review Output

Khi audit, mỗi finding có bốn phần:
- **Issue** — outcome/rule bị vi phạm;
- **Where** — file/component/route;
- **Severity** — critical / major / minor;
- **Fix** — một hành động cụ thể.

Severity:
- **critical:** block task, accessibility failure nghiêm trọng, mất dữ liệu, misleading trust/payment,
  unusable responsive/keyboard flow;
- **major:** phá project convention/design system, thiếu recovery/state quan trọng, motion/performance
  gây ảnh hưởng rõ;
- **minor:** polish/hierarchy/spacing/copy inconsistency không chặn task.

Không chấm điểm “đẹp/xấu” kiểu chủ quan nếu không gắn với outcome.

## External References

External UI/UX resources được dùng như **evidence/inspiration**, không phải authority.
Không tự gửi source code private, user data, secrets hay product-confidential content ra dịch vụ ngoài
chỉ để lấy design recommendation.

UI/UX Pro Max được native hóa chủ yếu ở:
- query contract;
- conditional reasoning;
- progressive design guidance;
- forms/charts/motion/a11y quick-reference mindset;
- master/override concept, nhưng project-local design system luôn thắng.

Không vendor catalog font/style/icon, Python search engine, GSAP/Phosphor hay generic palette chỉ vì
upstream có chúng.

## Progressive References

- Decision routing: `skill_view("ui-ux", "references/decision-contract.json")`
- Deep review checklist: `skill_view("ui-ux", "references/review-checklist.md")`

Chỉ load reference khi task cần, tránh làm context phình.

## Verification Checklist

- [ ] Đã đọc project rules/source of truth trước khi design.
- [ ] Đã xác định một dominant intent.
- [ ] Đã match decision contract thay vì chọn style trước.
- [ ] Đã reuse/compose trước khi thêm primitive.
- [ ] State/recovery phù hợp capability thực tế.
- [ ] Keyboard/focus/semantic/reduced-motion đã được xét.
- [ ] Responsive được kiểm ở breakpoint thực tế cần thiết.
- [ ] Command/test được lấy từ repo và chạy thật khi có quyền/tooling.
- [ ] Không tạo token/font/icon/design source of truth thứ hai.
- [ ] Không tuyên bố verified nếu chưa có evidence.
