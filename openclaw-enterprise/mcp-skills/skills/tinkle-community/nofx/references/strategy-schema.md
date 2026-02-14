# NOFX Strategy Configuration Schema

## Full Strategy Config

```json
{
  "strategy_type": "ai_trading",
  "language": "zh",
  
  "coin_source": {
    "source_type": "mixed",
    "static_coins": ["BTCUSDT", "ETHUSDT"],
    "excluded_coins": ["LUNAUSDT"],
    "use_ai500": true,
    "ai500_limit": 10,
    "use_oi_top": true,
    "oi_top_limit": 5,
    "use_oi_low": false,
    "oi_low_limit": 5
  },
  
  "indicators": {
    "klines": {
      "intervals": ["5m", "15m", "1h", "4h"],
      "limit": 100
    },
    "enable_raw_klines": true,
    "enable_ema": true,
    "enable_macd": true,
    "enable_rsi": true,
    "enable_atr": true,
    "enable_boll": true,
    "enable_volume": true,
    "enable_oi": true,
    "enable_funding_rate": true,
    "ema_periods": [20, 50],
    "rsi_periods": [7, 14],
    "atr_periods": [14],
    "boll_periods": [20],
    
    "nofxos_api_key": "cm_xxx",
    "enable_quant_data": true,
    "enable_quant_oi": true,
    "enable_quant_netflow": true,
    "enable_oi_ranking": true,
    "oi_ranking_duration": "1h",
    "oi_ranking_limit": 10,
    "enable_netflow_ranking": true,
    "netflow_ranking_duration": "1h",
    "netflow_ranking_limit": 10,
    "enable_price_ranking": true,
    "price_ranking_duration": "1h",
    "price_ranking_limit": 10
  },
  
  "risk_control": {
    "max_position_pct": 10,
    "max_total_position_pct": 50,
    "stop_loss_pct": 3,
    "take_profit_pct": 5,
    "max_daily_loss_pct": 10,
    "max_drawdown_pct": 15
  },
  
  "prompt_sections": {
    "role_definition": "你是一个专业的加密货币交易AI，专注于中短期趋势交易。",
    "trading_frequency": "每4小时分析一次市场，寻找高确定性机会。",
    "entry_standards": "只在RSI<30超卖或突破关键阻力位时考虑做多，RSI>70超买时考虑做空。",
    "decision_process": "1. 分析大周期趋势 2. 确认资金流向 3. 评估风险收益比 4. 确定仓位大小"
  },
  
  "custom_prompt": "额外注意：避免在重大消息公布前后交易。"
}
```

## Grid Trading Strategy

```json
{
  "strategy_type": "grid_trading",
  "language": "zh",
  
  "grid_config": {
    "symbol": "ETHUSDT",
    "grid_count": 20,
    "total_investment": 5000,
    "leverage": 3,
    "upper_price": 2200,
    "lower_price": 1800,
    "use_atr_bounds": false,
    "atr_multiplier": 2.0,
    "distribution": "uniform",
    "max_drawdown_pct": 10,
    "stop_loss_pct": 5,
    "daily_loss_limit_pct": 8,
    "use_maker_only": true,
    "enable_direction_adjust": true,
    "direction_bias_ratio": 0.7
  }
}
```

## Coin Source Types

| Type | Description | Use Case |
|------|-------------|----------|
| `static` | Fixed coin list | Known coins to trade |
| `ai500` | AI high potential coins | Follow AI signals |
| `oi_top` | OI increase ranking | Trending coins (long bias) |
| `oi_low` | OI decrease ranking | Declining coins (short bias) |
| `mixed` | Combination of sources | Diversified approach |

## Indicator Options

| Indicator | Periods | Description |
|-----------|---------|-------------|
| EMA | [20, 50] | Trend direction |
| RSI | [7, 14] | Overbought/oversold |
| MACD | default | Momentum |
| ATR | [14] | Volatility |
| BOLL | [20] | Support/resistance |

## Grid Distribution Types

| Type | Description |
|------|-------------|
| `uniform` | Equal spacing between grids |
| `gaussian` | Denser in the middle |
| `pyramid` | Denser at current price |

## Natural Language to Strategy Mapping

### Example 1: "Create a strategy for AI500 coins with RSI oversold entry"

```json
{
  "coin_source": {
    "source_type": "ai500",
    "use_ai500": true,
    "ai500_limit": 10
  },
  "indicators": {
    "enable_rsi": true,
    "rsi_periods": [14]
  },
  "prompt_sections": {
    "entry_standards": "Enter long when RSI < 30 (oversold)"
  }
}
```

### Example 2: "ETH grid trading between 1800-2200 with 20 grids"

```json
{
  "strategy_type": "grid_trading",
  "grid_config": {
    "symbol": "ETHUSDT",
    "grid_count": 20,
    "upper_price": 2200,
    "lower_price": 1800,
    "distribution": "uniform"
  }
}
```

### Example 3: "Track coins with large institution inflows"

```json
{
  "coin_source": {
    "source_type": "mixed",
    "use_ai500": false
  },
  "indicators": {
    "enable_quant_netflow": true,
    "enable_netflow_ranking": true,
    "netflow_ranking_duration": "1h",
    "netflow_ranking_limit": 10
  },
  "prompt_sections": {
    "entry_standards": "Focus on coins with institution inflow > $1M in the last hour"
  }
}
```
