# NOFX 多账户管理

## 多账户场景

1. **风险隔离** - 不同策略用不同账户
2. **多交易所** - 同时使用多个交易所
3. **资金分配** - 分散风险
4. **测试环境** - 主账户 + 测试账户

## 配置方式

### 同交易所多账户

在 Config 页面添加多个交易所配置，用不同名称区分：

```
binance-main       → 主账户
binance-test       → 测试账户
binance-grid       → 网格专用
```

### 多交易所

```
binance   → 主力交易
bybit     → 备用
okx       → 套利
gate      → 山寨币
```

## 账户命名建议

| 命名模式 | 示例 | 用途 |
|----------|------|------|
| `{交易所}-{用途}` | binance-main | 区分用途 |
| `{交易所}-{策略}` | binance-grid | 区分策略 |
| `{交易所}-{资金}` | binance-10k | 区分资金量 |

## Trader 与账户绑定

创建 Trader 时选择对应账户：

```
Trader: eth-hunter
├── AI Model: Claude
├── Exchange: binance-main    ← 选择账户
└── Strategy: ai500策略
```

## 资金分配建议

| 账户类型 | 资金比例 | 风险等级 |
|----------|----------|----------|
| 主账户 | 50-60% | 低风险策略 |
| 激进账户 | 20-30% | 高收益策略 |
| 测试账户 | 10-20% | 新策略测试 |

## 风险管理

### 单账户限制

- 最大持仓: 账户资金的 50%
- 单币最大: 账户资金的 20%
- 日亏损限: 账户资金的 10%

### 多账户总限

- 总暴露: 总资金的 70%
- 相关性: 避免所有账户持仓高度相关
- 监控: 汇总查看所有账户 P&L

## Dashboard 切换

在 Dashboard 页面顶部下拉菜单切换 Trader/账户：

```javascript
// 浏览器自动化切换账户
browser.act({kind: "click", ref: "traderSelector"})
browser.act({kind: "click", ref: "targetTrader"})
```

## API 多账户

调用不同账户的 API 时，使用对应的 API Key：

```bash
# 账户 A
curl -H "Authorization: Bearer $KEY_A" ...

# 账户 B
curl -H "Authorization: Bearer $KEY_B" ...
```

## 子账户功能 (交易所)

### Binance 子账户

1. 用户中心 → 子账户
2. 创建子账户
3. 划转资金
4. 生成子账户 API

### OKX 子账户

1. 用户中心 → 子账户管理
2. 创建交易子账户
3. 设置权限和限额

## 安全建议

1. **不同 IP 白名单** - 每个账户用不同服务器
2. **独立 2FA** - 每个账户独立验证
3. **权限最小化** - 只开必要权限
4. **定期审计** - 检查异常交易
