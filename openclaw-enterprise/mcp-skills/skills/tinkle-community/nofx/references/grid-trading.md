# NOFX 网格交易详细指南

## 网格交易原理

网格交易在设定的价格区间内自动低买高卖，适合震荡行情。

```
上界 $2200 ─────────────────
         │  卖出 │  卖出 │
         ├───────┼───────┤
         │       │       │
         ├───────┼───────┤  ← 网格
         │       │       │
         ├───────┼───────┤
         │  买入 │  买入 │
下界 $1800 ─────────────────
```

## 完整配置示例

### 示例 1: ETH 均匀网格

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "ETHUSDT",
    "grid_count": 20,
    "total_investment": 5000,
    "leverage": 3,
    "upper_price": 2200,
    "lower_price": 1800,
    "use_atr_bounds": false,
    "distribution": "uniform",
    "max_drawdown_pct": 10,
    "stop_loss_pct": 5,
    "daily_loss_limit_pct": 8,
    "use_maker_only": true,
    "enable_direction_adjust": false
  }
}
```

### 示例 2: BTC 自适应边界

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "BTCUSDT",
    "grid_count": 30,
    "total_investment": 10000,
    "leverage": 2,
    "use_atr_bounds": true,
    "atr_multiplier": 2.5,
    "distribution": "gaussian",
    "max_drawdown_pct": 15,
    "stop_loss_pct": 3,
    "use_maker_only": true,
    "enable_direction_adjust": true,
    "direction_bias_ratio": 0.6
  }
}
```

### 示例 3: 多头偏向网格

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "SOLUSDT",
    "grid_count": 15,
    "total_investment": 3000,
    "leverage": 5,
    "upper_price": 90,
    "lower_price": 70,
    "distribution": "pyramid",
    "enable_direction_adjust": true,
    "direction_bias_ratio": 0.7
  }
}
```

## 参数详解

### 基础参数

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `symbol` | 交易对 | BTCUSDT, ETHUSDT 等 |
| `grid_count` | 网格数量 | 10-50，越多越精细 |
| `total_investment` | 总投资额(USDT) | 根据资金量定 |
| `leverage` | 杠杆倍数 | 1-5x 建议 |

### 边界设置

| 参数 | 说明 |
|------|------|
| `upper_price` | 上边界价格 |
| `lower_price` | 下边界价格 |
| `use_atr_bounds` | 使用 ATR 自动计算边界 |
| `atr_multiplier` | ATR 倍数 (默认 2.0) |

### 分布类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| `uniform` | 均匀分布 | 无明确方向判断 |
| `gaussian` | 中间密集 | 预期价格在中间震荡 |
| `pyramid` | 当前价密集 | 预期小幅震荡 |

### 风控参数

| 参数 | 说明 | 建议值 |
|------|------|--------|
| `max_drawdown_pct` | 最大回撤止损 | 10-20% |
| `stop_loss_pct` | 单仓止损 | 3-5% |
| `daily_loss_limit_pct` | 日亏损限制 | 5-10% |

### 高级参数

| 参数 | 说明 |
|------|------|
| `use_maker_only` | 只挂 Maker 单，手续费更低 |
| `enable_direction_adjust` | 自动调整网格方向 |
| `direction_bias_ratio` | 方向偏向比例 (0.7 = 70%多/30%空) |

## 网格计算

### 每格间距

```
间距 = (上界 - 下界) / 网格数
例: (2200 - 1800) / 20 = $20/格
```

### 每格仓位

```
每格投资 = 总投资 / 网格数 * 杠杆
例: 5000 / 20 * 3 = $750/格
```

### 预期收益

```
单次套利 = 每格投资 * 间距%
例: 750 * (20/2000) = $7.5/次
```

## 适用行情

| 行情类型 | 适合网格 | 建议 |
|----------|----------|------|
| 震荡横盘 | ✅ 非常适合 | 标准网格 |
| 缓慢上涨 | ✅ 适合 | 多头偏向网格 |
| 缓慢下跌 | ⚠️ 谨慎 | 空头偏向 + 小仓位 |
| 剧烈波动 | ❌ 不适合 | 暂停网格 |
| 单边行情 | ❌ 不适合 | 使用趋势策略 |

## 常见问题

### Q: 网格数量怎么选？

- 波动大: 10-15 格，间距大
- 波动小: 25-50 格，间距小
- 资金少: 10-20 格
- 资金多: 30-50 格

### Q: 边界怎么设？

1. 看近期支撑/阻力位
2. 用 ATR 自动计算 (推荐)
3. 上下各留 10-20% 空间

### Q: 什么时候停止？

- 价格突破边界
- 达到最大回撤
- 单边行情出现
- 重大消息前
