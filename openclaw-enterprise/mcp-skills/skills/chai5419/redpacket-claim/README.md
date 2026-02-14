# 红包自动领取技能 (RedPacket Claim Skill)

全自动红包领取技能，支持微信、支付宝、QQ、抖音等多平台。

## 🚀 功能特性

- **全自动检测**：自动识别红包口令并触发领取
- **多平台支持**：微信、支付宝、QQ、抖音、快手等
- **智能路由**：根据上下文选择最佳领取平台
- **安全可靠**：完善的隐私保护和风控机制
- **易于扩展**：插件化架构，支持新平台快速接入

## 📦 文件结构

```
redpacket-claim/
├── SKILL.md                 # 技能主文档
├── README.md                # 本文件
├── _meta.json              # 技能元数据
├── scripts/
│   ├── __init__.py
│   └── claim_redpacket.py   # 主领取脚本
└── references/
    ├── platforms.md        # 平台技术文档
    └── security.md        # 安全与隐私指南
```

## 🔧 快速开始

### 1. 环境要求
- Python 3.8+
- OpenClaw 2026.2.2+
- 网络访问权限

### 2. 配置文件（可选）
创建配置文件 `/root/.openclaw/redpacket-config.json`：
```json
{
  "platforms": ["wechat", "alipay", "qq"],
  "priority": "wechat",
  "timeout": 30,
  "max_retries": 3,
  "browser": "chrome",
  "headless": false
}
```

### 3. 技能触发
当用户输入以下内容时自动触发：
- "红包口令：天天开心"
- "抢红包：恭喜发财"
- "领取红包：新年快乐"
- 直接输入口令："大吉大利"

## 🎯 使用示例

### 场景1：直接输入口令
**用户输入**：
```
大吉大利
```

**AI自动响应**：
```
检测到红包口令：大吉大利
正在尝试领取...
✅ 成功在微信领取红包！
💰 金额：8.88元
⏰ 领取时间：2026-02-11 20:10:23
```

### 场景2：命令行调用
```bash
# 基本使用
python3 scripts/claim_redpacket.py --code "天天开心"

# 指定平台
python3 scripts/claim_redpacket.py --code "恭喜发财" --platform alipay

# 详细模式
python3 scripts/claim_redpacket.py --code "新年快乐" --verbose --retry 3
```

## ⚙️ 配置说明

### 环境变量
```bash
export REDPACKET_CONFIG='{"platforms": ["wechat", "alipay"], "timeout": 30}'
```

### 脚本参数
| 参数 | 缩写 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `--code` | `-c` | 是 | - | 红包口令 |
| `--platform` | `-p` | 否 | `auto` | 目标平台 |
| `--config` | `-C` | 否 | `~/.openclaw/redpacket-config.json` | 配置文件 |
| `--timeout` | `-t` | 否 | `30` | 超时时间（秒） |
| `--retry` | `-r` | 否 | `2` | 重试次数 |
| `--headless` | `-H` | 否 | `false` | 无头模式 |
| `--verbose` | `-v` | 否 | `false` | 详细日志 |

## 🛡️ 安全注意事项

### 重要提醒
1. **遵守平台规则**：不要违反微信、支付宝等平台的用户协议
2. **合理使用**：避免频繁操作触发风控机制
3. **隐私保护**：妥善保管个人账号信息
4. **法律合规**：仅用于个人学习和研究目的

### 风险控制
- 单用户频率限制：60次/小时
- 单IP频率限制：100次/小时
- 异常行为自动暂停
- 详细操作日志记录

## 🔍 故障排除

### 常见问题
1. **领取失败**：检查网络连接和登录状态
2. **口令无效**：确认口令未过期且格式正确
3. **平台不支持**：查看支持的平台列表
4. **频率限制**：等待限制解除或切换账号

### 调试模式
```bash
python3 scripts/claim_redpacket.py --code "测试" --platform wechat --verbose
```

### 查看日志
```bash
tail -f /tmp/redpacket-claim.log
```

## 📚 详细文档

### 平台技术文档
- [平台接口说明](references/platforms.md)
- 各平台技术实现细节
- 接口调用示例

### 安全指南
- [安全与隐私](references/security.md)
- 风险控制策略
- 合规要求说明

## 🤝 贡献指南

### 添加新平台
1. 在 `references/platforms.md` 中添加平台文档
2. 在 `scripts/platforms/` 下添加平台实现
3. 更新配置文件验证逻辑

### 报告问题
1. 在日志中查找错误信息
2. 提供复现步骤
3. 包含相关配置信息

## 📄 许可证

仅供学习和研究使用，请遵守相关法律法规和平台规定。

## ⚠️ 免责声明

本技能仅用于技术学习和研究，不对以下情况负责：
- 平台封号等后果
- 领取成功率
- 数据安全问题
- 法律合规问题

用户需自行承担使用风险。

---

**作者**：OpenClaw Skill Creator  
**版本**：1.0.0  
**最后更新**：2026-02-11