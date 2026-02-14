# NOFX 支持的交易所

## CEX 中心化交易所

| 交易所 | 注册链接 (返佣) | 状态 |
|--------|----------------|------|
| **Binance** | [注册](https://www.binance.com/join?ref=NOFXENG) | ✅ 支持 |
| **Bybit** | [注册](https://partner.bybit.com/b/83856) | ✅ 支持 |
| **OKX** | [注册](https://www.okx.com/join/1865360) | ✅ 支持 |
| **Bitget** | [注册](https://www.bitget.com/referral/register?from=referral&clacCode=c8a43172) | ✅ 支持 |
| **KuCoin** | [注册](https://www.kucoin.com/r/broker/CXEV7XKK) | ✅ 支持 |
| **Gate.io** | [注册](https://www.gatenode.xyz/share/VQBGUAxY) | ✅ 支持 |

## DEX 去中心化永续交易所

| 交易所 | 注册链接 | 状态 |
|--------|----------|------|
| **Hyperliquid** | [注册](https://app.hyperliquid.xyz/join/AITRADING) | ✅ 支持 |
| **Aster DEX** | [注册](https://www.asterdex.com/en/referral/fdfc0e) | ✅ 支持 |
| **Lighter** | [注册](https://app.lighter.xyz/?referral=68151432) | ✅ 支持 |

## 支持的 AI 模型

| 模型 | 获取 API Key | 推荐 |
|------|-------------|------|
| **DeepSeek** | [获取](https://platform.deepseek.com) | ⭐ 性价比高 |
| **Qwen** | [获取](https://dashscope.console.aliyun.com) | 中文优化 |
| **OpenAI (GPT)** | [获取](https://platform.openai.com) | 通用强 |
| **Claude** | [获取](https://console.anthropic.com) | 推理强 |
| **Gemini** | [获取](https://aistudio.google.com) | 免费额度 |
| **Grok** | [获取](https://console.x.ai) | 新兴 |
| **Kimi** | [获取](https://platform.moonshot.cn) | 中文强 |

## 交易所 API 配置

### Binance

1. 登录 Binance
2. 进入 API 管理: 用户中心 → API 管理
3. 创建 API → 系统生成
4. 开启权限:
   - ✅ 读取
   - ✅ 现货和杠杆交易
   - ✅ 合约交易
5. IP 白名单 (推荐): 添加服务器 IP
6. 复制 API Key 和 Secret

### Bybit

1. 登录 Bybit
2. 进入 API: 账户 → API 管理
3. 创建新 API
4. 权限设置:
   - ✅ 合约 - 订单
   - ✅ 合约 - 仓位
5. 绑定 IP (可选)

### OKX

1. 登录 OKX
2. 进入 API: 用户中心 → API
3. 创建 V5 API
4. 权限:
   - ✅ 读取
   - ✅ 交易
5. 设置 Passphrase (必须记住)

### Gate.io

1. 登录 Gate.io
2. 进入 API: 用户中心 → API 管理
3. 创建 API Key
4. 权限:
   - ✅ 现货交易
   - ✅ 合约交易
   - ✅ 提现 (可选，建议关闭)

### Hyperliquid

1. 访问 [Hyperliquid](https://app.hyperliquid.xyz)
2. 连接钱包
3. 进入 API: 设置 → API
4. 创建 API Key (需要签名授权)

### Aster DEX

1. 访问 [Aster DEX](https://www.asterdex.com)
2. 连接钱包
3. 设置 → API 管理
4. 创建交易 API

## 安全建议

1. **开启 IP 白名单** - 只允许服务器 IP 访问
2. **最小权限原则** - 只开启需要的权限
3. **关闭提现权限** - 除非绝对必要
4. **定期轮换 API Key** - 每月更新一次
5. **使用独立子账户** - 隔离交易资金
6. **设置合理杠杆** - 建议 ≤5x
