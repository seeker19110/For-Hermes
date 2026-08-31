---
name: project-harness-engineering
description: "Dùng khi thiết kế hoặc audit project harness cho AI."
version: 0.1.0
author: liend, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [project-harness, coding-agents, context, guardrails, verification]
    related_skills: [hermes-agent, safe-ai-state-authority]
---

# Project Harness Engineering

Skill này giúp khảo sát, thiết kế, triển khai và audit môi trường làm việc cấp project cho coding agent. Mục tiêu là làm project dễ hiểu, hành động có giới hạn và kết quả có thể kiểm chứng; không thay thế kiến trúc, CI hay security review của project.

## When to Use

- Người dùng hỏi project harness hoặc harness engineering là gì.
- Cần tạo hay cải thiện `AGENTS.md`, `.hermes.md`, `CLAUDE.md` hoặc rule tương đương.
- Agent thường dùng sai command, vi phạm convention, sửa nhầm phạm vi hoặc báo hoàn thành khi chưa test.
- Cần chuẩn hóa workflow AI cho một repository hay monorepo.
- Cần audit mức sẵn sàng của project trước khi giao việc dài hạn hoặc đa agent.

Không dùng skill này như lý do để viết thêm tài liệu khi một test, type system, permission gate hoặc CI check có thể cưỡng chế quy tắc chắc chắn hơn.

## Mô hình

```text
Coding agent = Model + Runtime harness + Project harness

Project harness
= Context + Knowledge + Tools + Permissions
+ Workflow + State + Verification + Recovery
```

Phân biệt rõ:

- **Model:** suy luận và sinh nội dung.
- **Runtime harness:** quản lý vòng lặp agent, tool calls, context, sandbox và approval.
- **Project harness:** artifact và control dành riêng cho repository.
- **Orchestrator:** điều phối nhiều run, agent, worktree hoặc hàng đợi.

## Thành phần cần khảo sát

1. **Context files:** `AGENTS.md`, `.hermes.md`, `CLAUDE.md`, rules theo tool.
2. **Knowledge:** README, architecture docs, ADR, business rules, code map.
3. **Commands:** setup, build, lint, typecheck, test, run, release.
4. **Tools:** script deterministic, CLI nội bộ, MCP hoặc integration cần thiết.
5. **Authority:** phạm vi được đọc/sửa, approval, secret handling, thao tác bị cấm.
6. **Workflow:** branch, commit, PR, review, CI và release.
7. **State:** plan, task status, decision log, known debt và handoff.
8. **Verification:** acceptance criteria, tests, structural checks và bằng chứng chạy thật.
9. **Recovery:** rollback, retry an toàn, xử lý test fail và escalation.

## Procedure

### 1. Khảo sát repository trước khi đề xuất

- Dùng `search_files(target='files')` để lập bản đồ các context file, manifest, lockfile, CI, docs, scripts và test hiện có.
- Dùng `read_file` để đọc đúng các file liên quan; không suy diễn command từ tên project.
- Dùng `terminal` cho trạng thái Git, command discovery và kiểm tra executable thực tế.
- Ghi rõ thông tin nào đã xác minh, thông tin nào còn thiếu.

Hoàn thành khi mọi đề xuất đều truy nguyên được về artifact hiện có, yêu cầu người dùng hoặc failure thực tế.

### 2. Lập bản đồ failure → control

Với mỗi lỗi hoặc rủi ro, chọn control nhỏ nhất có hiệu lực:

| Failure | Control ưu tiên |
|---|---|
| Agent không biết project nằm ở đâu | Code map ngắn trong context file |
| Dùng sai package manager/command | Command chuẩn + lockfile + script |
| Quên convention | Rule ngắn; lint nếu kiểm tra được |
| Vi phạm ranh giới kiến trúc | Structural test hoặc custom lint |
| Báo xong nhưng code hỏng | Verification gate bắt buộc |
| Sửa ngoài phạm vi | Path scope + diff check + approval |
| Mất tiến độ giữa các phiên | Plan/state artifact được version hóa |
| Lặp side effect | Idempotency, receipt và read-back |
| Lệnh nguy hiểm | Permission gate hoặc blocking hook |

Ưu tiên theo thứ tự: **cưỡng chế deterministic → chỉ dẫn ngắn → tài liệu tham khảo**. Không biến mọi ý tưởng thành rule.

### 3. Thiết kế context theo nguyên tắc “bản đồ, không phải bách khoa”

Context file gốc nên ngắn và trả lời:

1. Project làm gì và source of truth ở đâu?
2. Cấu trúc thư mục chính và ranh giới module là gì?
3. Setup/build/lint/typecheck/test bằng command nào?
4. Những invariant và vùng cấm sửa nào quan trọng?
5. Quy trình branch, commit, PR và CI ra sao?
6. Bằng chứng nào bắt buộc trước khi tuyên bố hoàn thành?
7. Khi thiếu dữ kiện hoặc gặp lỗi phải escalation thế nào?

Đưa chi tiết dài vào `docs/`, script hoặc skill và liên kết từ context file. Với Hermes, chọn `.hermes.md` khi cần kế thừa theo cây thư mục; chọn `AGENTS.md` khi cần khả năng dùng qua nhiều coding agent. Không tạo đồng thời nhiều file chứa rule trùng hoặc mâu thuẫn.

### 4. Chuyển quy tắc quan trọng thành executable guardrail

- Dùng test, typecheck, lint, schema validation hoặc CI thay cho lời nhắc khi có thể.
- Viết thông báo lỗi chỉ rõ cách sửa để feedback quay lại agent có ích.
- Chặn destructive action ở permission/hook layer, không chỉ ghi “hãy cẩn thận”.
- External write phải có explicit scope và được đọc lại đúng target trước khi báo thành công.
- Không cấp quyền rộng hơn nhu cầu của task; áp dụng `safe-ai-state-authority` cho state và side effect nhạy cảm.

Hoàn thành khi mỗi invariant mức cao có ít nhất một cơ chế phát hiện hoặc ngăn chặn rõ ràng.

### 5. Tạo vòng kiểm chứng

Thiết kế vòng lặp:

```text
Inspect → Plan → Change → Format → Static checks
→ Focused tests → Broader tests → Diff review → Evidence
```

Mỗi acceptance criterion phải ánh xạ tới một verification command hoặc kiểm tra quan sát được. Không chấp nhận câu “đã sửa” nếu thiếu output thực tế.

### 6. Triển khai tăng dần

Mức khởi đầu tối thiểu:

- Một context file ngắn.
- Command setup/build/test đã được chạy thử.
- CI cơ bản.
- Quy tắc Git và phạm vi sửa.
- Definition of done có bằng chứng.

Chỉ thêm skill, hook, MCP, subagent hoặc custom lint khi failure thực tế chứng minh nhu cầu. Mỗi thay đổi harness phải được review và version-control như code.

### 7. Audit sau triển khai

Chấm từng mục `0–2`:

- `0`: không tồn tại.
- `1`: có nhưng thủ công, mơ hồ hoặc chưa kiểm chứng.
- `2`: rõ ràng, chạy được và có bằng chứng.

Các mục: Context, Knowledge, Commands, Authority, Workflow, State, Verification, Recovery. Tổng tối đa 16:

- `0–5`: agent-hostile.
- `6–10`: dùng được cho task nhỏ có giám sát.
- `11–13`: sẵn sàng cho task vừa.
- `14–16`: mạnh; vẫn cần đánh giá rủi ro theo từng task.

Điểm số không thay thế bằng chứng. Báo kèm gap, rủi ro, control đề xuất và thứ tự ưu tiên.

## Mẫu đầu ra

Khi nghiên cứu hoặc audit, trả về:

```md
## Hiện trạng đã xác minh
- ...

## Failure/risk → control
| Rủi ro | Bằng chứng | Control hiện có | Khoảng trống | Đề xuất |

## Điểm harness
| Thành phần | Điểm 0–2 | Bằng chứng |

## Thay đổi ưu tiên
1. P0 — ...
2. P1 — ...
3. P2 — ...

## Verification
- Command/check đã chạy: ...
- Kết quả: ...
- Chưa xác minh: ...
```

Khi triển khai, tạo artifact thật, chạy command kiểm chứng và báo ngắn: file nào thay đổi, kiểm tra nào đã qua, còn blocker nào.

## Pitfalls

- `AGENTS.md` dài không đồng nghĩa harness tốt; context dư làm loãng quy tắc quan trọng.
- Tài liệu stale nguy hiểm hơn thiếu tài liệu vì tạo cảm giác chắc chắn giả.
- Rule trong prompt vẫn mang tính xác suất; invariant quan trọng phải được cưỡng chế bằng code hoặc policy.
- Nhiều context file trùng nhau có thể tạo xung đột và hành vi khó dự đoán.
- Cài nhiều MCP/tool làm tăng attack surface và chi phí chọn tool.
- Self-review không thay thế independent test, CI hoặc human judgment ở vùng rủi ro cao.
- Không copy nguyên harness từ project khác mà chưa kiểm tra stack, workflow và authority của project hiện tại.
- Không dùng điểm maturity để tuyên bố project an toàn tuyệt đối.

## Verification Checklist

- [ ] Đã đọc artifact hiện có trước khi sửa.
- [ ] Context file là bản đồ ngắn, không phải bản sao toàn bộ docs.
- [ ] Command ghi trong harness đã được chạy hoặc đánh dấu chưa xác minh.
- [ ] Mỗi invariant quan trọng có automated check hoặc lý do rõ ràng nếu chưa có.
- [ ] Scope quyền và destructive actions có gate.
- [ ] Acceptance criteria ánh xạ tới bằng chứng kiểm chứng.
- [ ] Git diff chỉ chứa thay đổi thuộc phạm vi.
- [ ] Không tuyên bố hoàn thành nếu test/CI bắt buộc chưa xanh.
