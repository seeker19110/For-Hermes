# Fanfic-Writer Skill - FanFiction Writer Skill
通过 AI agent管道流水线实现从题材到完整小说的自动化小说创作

---

## 📦 安装方法

### 1. 复制 Skill 文件
将 `fanfic-writer.skill` 复制到 OpenClaw 的 skills 目录：

**Windows:**
```
C:\Users\<用户名>\clawd\skills\
```

**Linux/macOS:**
```
~/.openclaw/skills/
```

### 2. 解压安装
```bash
# 进入 skills 目录
cd <skills 目录>

# 解压 skill 文件（其实就是一个 zip）
unzip fanfic-writer.skill
# 或 Windows: 右键解压 fanfic-writer.skill

# 确保目录结构如下：
skills/
└── fanfic-writer/
    ├── SKILL.md
    ├── references/
    │   └── prompts.md
    └── scripts/
        ├── state_manager.py
        ├── session_context.py
        ├── token_tracker.py
        ├── tomato_fetch.py
        ├── outline_generator.py
        ├── chapter_writer.py
        └── merge_book.py
```

### 3. 重启 OpenClaw
安装完成后重启 OpenClaw，skill 会自动加载。

---

## 🚀 快速开始

### 方式一：直接指定题材
```
我想写一本[玄幻]小说
```
```
开始创作一部[末世求生]题材的小说，大约30万字
```

### 方式二：让 AI 推荐题材
```
开始写小说
```
AI 会引导你选择题材、生成大纲。

### 方式三：断点续写
```
继续写[书名]
```
从上次中断的地方继续写作。

---

## 📖 使用流程

###  Phase 1: 题材选择
- 指定题材或使用示例
- AI 分析热门题材特点

###  Phase 2: 生成主大纲
- 生成主线梗概
- 确认后保存到 `1-main-outline.md`

###  Phase 3: 章节规划
- 将大纲扩展为详细章节规划
- 确认后保存到 `2-chapter-plan.json`

###  Phase 4: 世界观设定
- 生成世界观、角色、力量体系等
- 确认后保存到 `3-world-building.md`

###  Phase 5: 逐章写作（核心）
每章的工作流程：
1. **生成本章详细大纲** → 确认
2. **起草正文**（≤2000字分段）
3. **质量检查**（设定一致性、文笔）
4. **保存章节** → `chapters/第XXX章_章节名.txt`
5. **记录 Token 消耗**

重复直到所有章节完成。

###  Phase 6: 合并与整书检查
```
合并成书 [书名]
```
1. 合并所有章节为完整小说
2. **整书质量检查**：
   - 设定一致性
   - 大纲符合度
   - 剧情逻辑
   - 人物性格
   - 伏笔回收
3. 生成检查报告

---

## 🗂️ 文件结构说明

创作的小说会保存在：
```
novels/
└── {时间戳}_{书名}/
    ├── 0-book-config.json      # 总配置
    ├── 1-main-outline.md       # 主大纲
    ├── 2-chapter-plan.json     # 章节规划
    ├── 3-world-building.md     # 世界观设定
    ├── 4-writing-state.json    # 写作进度（断点续写）
    ├── 5-chapter-outlines.json # 各章详细大纲索引
    ├── 6-session-context.json  # 短期记忆（防中断）
    ├── token-report.json       # Token消耗统计
    ├── chapters/               # 章节正文
    │   ├── 第001章_开篇.txt
    │   └── 第002章_发展.txt
    └── final/
        ├── {书名}_完整版.txt   # 合并后的完整小说
        ├── full_book_check.json      # 整书检查结果
        └── full_book_check_prompt.txt # 整书检查提示词
```

---

## 🎨 写作风格特而且这个性

本 skill 专门针对**去 AI 味**进行了优化：

- ✅ **不过度解释** — 适当留白
- ✅ **避免堆砌修辞** — 不要每个动作都加比喻
- ✅ **保持镜头感** — 第三方可见视角描述
- ✅ **长短句结合** — 避免一成不变的节奏
- ✅ **允许不完美** — 文字有"破绽"更真实

这些风格要求已内置在提示词中，无需额外设置。

---

## 📊 Token & 成本统计

写作过程中会自动记录：
- 每步操作的 token 消耗
- 总消耗统计
- 预估成本（USD）

查看报告：
```
查看 {书名} 的 token 消耗
```

报告保存于：`novels/{书名}/token-report.json`

---

## 🔧 断点续写

如果写作中断，可以使用：
```
继续写[书名]
```

AI 会：
1. 读取 `6-session-context.json` 恢复会话状态
2. 读取 `4-writing-state.json` 定位进度
3. 确认上次待确认的内容
4. 从断点继续

---

## ⚙️ 高级功能

### 手动运行脚本
```bash
# 创建新书
cd scripts
python state_manager.py create "我的小说"

# Token 统计
python token_tracker.py <小说目录> summary

# 整书检查
python merge_book.py <小说目录> check
```

### 自定义提示词
修改 `references/prompts.md` 可以自定义：
- 大纲生成提示词
- 写作风格要求
- 质量检查标准

---

## 💡 创作建议

| 建议 | 说明 |
|------|------|
| 分阶段确认 | 大纲、设定都先确认再写作，避免返工 |
| 控制章节 | 每章≤2000字，超过会分片处理 |
| 及时检查 | 每章写完做质量检查，防止问题累积 |
| 整书检查 | 最终必须做整书检查，确保前后一致 |

---

## 🐛 故障排查

### Skill 没加载？
- 检查目录结构是否正确
- 重启 OpenClaw

### 中文显示乱码？
- 确保编辑器使用 UTF-8 编码
- Windows 用户建议用 VS Code

### Token 消耗过高？
- 减少单次请求字数
- 增加质量检查频率
- 使用更高效模型

---

## 📄 许可证

MIT License - 可自由使用、修改、分发。

---

## 🙏 致谢

基于 OpenClaw platform 开发，感谢社区支持。

**Happy Writing!** 🎉