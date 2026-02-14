# NOFX Webhook 通知集成

## 支持的通知渠道

| 渠道 | 用途 | 配置方式 |
|------|------|----------|
| Telegram | 即时消息 | Bot Token + Chat ID |
| Discord | 团队协作 | Webhook URL |
| Slack | 工作通知 | Webhook URL |
| 自定义 | 第三方系统 | HTTP POST |

## Telegram 通知

### 通过 Clawdbot

已集成 Clawdbot，直接使用 cron job 发送：

```json
{
  "payload": {
    "deliver": true,
    "channel": "telegram",
    "to": "YOUR_CHAT_ID"
  }
}
```

### 直接调用 Telegram API

```bash
TELEGRAM_BOT_TOKEN="your_bot_token"
CHAT_ID="your_chat_id"
MESSAGE="🚀 NOFX Alert: ETH 突破 $2000"

curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -d "chat_id=$CHAT_ID" \
  -d "text=$MESSAGE" \
  -d "parse_mode=Markdown"
```

## Discord Webhook

### 创建 Webhook

1. 服务器设置 → 整合 → Webhook
2. 创建 Webhook，复制 URL

### 发送通知

```bash
DISCORD_WEBHOOK="https://discord.com/api/webhooks/xxx/yyy"

curl -H "Content-Type: application/json" \
  -X POST "$DISCORD_WEBHOOK" \
  -d '{
    "content": "🚀 NOFX Alert",
    "embeds": [{
      "title": "AI500 新信号",
      "description": "POWER 入榜，评分 88.5",
      "color": 5763719
    }]
  }'
```

## Slack Webhook

### 创建 Webhook

1. Slack App → Incoming Webhooks
2. 添加到频道，复制 URL

### 发送通知

```bash
SLACK_WEBHOOK="https://hooks.slack.com/services/xxx/yyy/zzz"

curl -X POST "$SLACK_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "🚀 NOFX Alert: ETH 机构流入 $10M"
  }'
```

## 自定义 Webhook

### 通用 HTTP POST

```bash
WEBHOOK_URL="https://your-server.com/webhook"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "ai500_signal",
    "symbol": "POWER",
    "score": 88.5,
    "timestamp": "2026-02-12T12:00:00Z"
  }'
```

## Clawdbot 集成示例

### 价格告警

```bash
# 监控 BTC 价格，突破 70000 时通知
if [ $(curl -s "https://nofxos.ai/api/coin/BTC?auth=$KEY" | jq '.data.price') -gt 70000 ]; then
  # 发送 Telegram 通知
  curl -s "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
    -d "chat_id=$CHAT_ID" \
    -d "text=🚀 BTC 突破 $70,000!"
fi
```

### AI500 新币告警

```bash
# 检查 AI500 新币
NEW_COINS=$(curl -s "https://nofxos.ai/api/ai500/list?auth=$KEY" | \
  jq -r '.data.coins[] | select(.start_time > (now - 3600)) | .pair')

if [ -n "$NEW_COINS" ]; then
  # 发送通知
  MESSAGE="🆕 AI500 新入榜: $NEW_COINS"
  # ... 发送到 Telegram/Discord/Slack
fi
```

### 大额资金流告警

```bash
# 检查机构资金流入 > $10M
BIG_FLOWS=$(curl -s "https://nofxos.ai/api/netflow/top-ranking?auth=$KEY&limit=5&duration=1h&type=institution" | \
  jq -r '.data.netflows[] | select(.amount > 10000000) | "\(.symbol): $\(.amount/1000000)M"')

if [ -n "$BIG_FLOWS" ]; then
  MESSAGE="💰 大额机构流入:\n$BIG_FLOWS"
  # ... 发送通知
fi
```

## 通知模板

### 行情汇报模板

```
📊 NOFX 市场行情 | {time}

🤖 AI500信号
{ai500_list}

💰 机构流入 TOP5
{flow_list}

🚀 1h涨幅 TOP5
{gainers_list}

⚠️ 风险提示
{alerts}
```

### 交易信号模板

```
🎯 交易信号 | {symbol}

方向: {direction}
入场: ${entry_price}
止损: ${stop_loss}
止盈: ${take_profit}
仓位: {position_size}%

AI评分: {ai_score}
资金流: {fund_flow}
```

### P&L 汇报模板

```
💰 {trader_name} 日报

权益: ${equity}
P&L: ${pnl} ({pnl_pct}%)
持仓: {positions_count}

今日交易: {trades_count}
胜率: {win_rate}%
```
