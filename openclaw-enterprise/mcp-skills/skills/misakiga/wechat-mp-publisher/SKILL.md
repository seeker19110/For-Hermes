---
name: wechat-mp-publisher
version: 2.0.1
description: 远程微信公众号发布技能。通过 HTTP MCP 解决家用宽带 IP 变动问题，支持大文件上传、多主题排版与一键发布。
homepage: https://github.com/caol64/wenyan-mcp
metadata:
  openclaw:
    emoji: "🚀"
    category: publishing
  clawdbot:
    emoji: "🚀"
    requires:
      bins: ["mcporter", "curl"]
    install:
      - id: "node"
        kind: "node"
        package: "mcporter"
        bins: ["mcporter"]
        label: "安装 MCP 客户端 (mcporter)"
---

# 微信公众号远程发布 (Remote Publisher)

**核心痛点解决**：家用宽带 IP 频繁变动，无法固定添加到公众号白名单？
本技能通过远程 `wenyan-mcp` 服务中转，让你的本地 OpenClaw 也能稳定发布文章，无需本地 IP 权限！

## 🌟 架构优势

- **IP 漫游无忧**：仅需将远程 MCP 服务器 IP 加入白名单，无论你在家里、咖啡厅还是 4G 热点，都能随时发布。
- **资源集中管理**：排版主题、样式配置统一在服务端管理，多设备共享。
- **大文件支持**：内置 `upload_file` 优化通道，稳定传输高清大图和长文。
- **兼容性强**：完全兼容 wenyan-cli 的 Frontmatter 语法和排版风格。

## ⚙️ 快速配置

### 1. 连接远程服务 (mcp.json)

确保 `/root/.openclaw/mcp.json` 指向你的远程 MCP 实例：

```json
{
  "mcpServers": {
    "wenyan-mcp": {
      "name": "公众号远程助手",
      "transport": "sse",
      "url": "http://<your-remote-server-ip>:3000/sse",
      "headers": {
        "X-API-Key": "<optional-api-key>"
      }
    }
  }
}
```

### 2. 准备凭证 (Env / TOOLS.md)

发布时需提供公众号凭证（建议写入 `~/.bashrc` 或 `TOOLS.md`）：

```bash
export WECHAT_APP_ID="wx..."
export WECHAT_APP_SECRET="cx..."
```

## 🚀 使用指南

### 方式 A: 智能助手 (推荐)

直接对我说：
> "帮我把 `path/to/article.md` 发布到公众号，使用默认主题。"

我会自动：
1. 读取文件并检查 Frontmatter
2. 上传文件到远程 MCP
3. 调用发布接口并返回草稿链接

### 方式 B: 命令行脚本 (高级)

我们提供了封装好的脚本 `scripts/publish-remote.sh`，体验与本地 CLI 一致：

```bash
# 赋予执行权限
chmod +x scripts/publish-remote.sh

# 发布文章
./scripts/publish-remote.sh ./my-post.md

# 指定主题 (lapis)
./scripts/publish-remote.sh ./my-post.md lapis
```

## 📝 Markdown 规范

与标准 wenyan-cli 一致，头部必须包含元数据：

```markdown
---
title: 我的精彩文章
cover: https://example.com/cover.jpg
---

# 正文开始
...
```

*提示：`cover` 推荐使用图床链接，以确保远程服务器能正确下载封面。*

## 🛠️ 故障排查

| 现象 | 原因 | 解决方案 |
| :--- | :--- | :--- |
| **IP not in whitelist** | 远程服务器 IP 未加白 | 登录公众号后台 -> 基本配置 -> IP 白名单，添加 **MCP 服务器的公网 IP** (非本机 IP) |
| **upload failed** | 文件过大或网络波动 | 尝试手动使用 `curl` 上传接口，或检查 MCP 服务日志 |
| **cover not found** | 封面图无法访问 | 确保 `cover` 字段是公网可访问的 URL，或 MCP 服务端能读取的绝对路径 |

## 📂 资源索引

- **[主题列表](references/themes.md)**: 查看支持的排版主题
- **[完整排查指南](references/troubleshooting.md)**: 更多错误码解析
