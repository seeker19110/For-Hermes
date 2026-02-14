# OKX Trader Skill

A professional-grade automated trading agent skill for OKX. This skill enables the AI agent to manage grid trading strategies, monitor account performance, and handle market execution with built-in safety protocols.

## System Capabilities

### 1. Dual-Grid Execution
The agent operates two concurrent strategies:
- **Macro Grid (Main):** Heavy positions for capturing major trend movements.
- **Micro Grid:** High-frequency scalp positions for extracting profit from minor volatility.

### 2. Auto-Trailing (Rescale) Logic
The skill automatically detects when the market price drifts outside the active grid range. It performs a "Rescale" operation:
- Cancels all legacy orders associated with the bot.
- Recalculates and re-centers the grid layout based on the current market ticker.
- Persists new range settings to `grid_settings.json`.

### 3. Risk Management & Protection
- **Cost Basis Guard:** Prevents the agent from placing sell orders below the average entry price (including a minimum profit buffer).
- **Inventory Control:** Respects `maxPosition` limits to prevent over-leveraging during extended downtrends.
- **Order Throttling:** Built-in delays and batch execution to prevent rate-limiting and improve efficiency.

## Available Tools

### `okx_report`
Generates a highly condensed PnL and status report.

### `okx_grid_maintain`
The core execution tool that maintains the grid structure.

## Internal Dependencies
Requires the following local files in `/root/.openclaw/workspace/okx_data/`:
- `config.json`: API credentials.
- `grid_settings.json`: Strategy parameters.

## ⚠️ RISK WARNING
Trading cryptocurrencies involves significant risk. This skill is provided "as is" without warranties.
- **Simulation First:** Always test with `OKX_IS_SIMULATION=true` before using real funds.
- **Permissions:** Use API keys with "Trade" permissions only. **Disable "Withdrawal" permissions.**

---

# OKX Trader Skill (中文说明)

一个专为 OKX 交易所设计的专业级自动化交易技能。该技能使 AI 代理能够管理网格交易策略、监控账户表现，并具备内置安全协议的行情执行能力。

## 系统功能

### 1. 双层网格执行
代理同时运行两种策略：
- **大网格 (Main):** 使用较大仓位，旨在捕捉主要的市场趋势运动。
- **小网格 (Micro):** 高频剥头皮仓位，旨在从微小的波动中提取利润。

### 2. 自动跟随 (Rescale) 逻辑
技能会自动检测市场价格何时偏离活跃网格区间。它执行“Rescale”操作：
- 取消与该机器人相关的所有旧订单。
- 根据当前市场价格重新计算并居中网格布局。
- 将新的区间设置持久化到 `grid_settings.json`。

### 3. 风险管理与保护
- **成本基准保护:** 防止代理以低于平均入场价的价格下达卖单（包括最小利润缓冲）。
- **库存控制:** 遵守 `maxPosition` 限制，防止在持续下跌趋势中过度加仓。
- **订单节流:** 内置延迟和批量执行，防止 API 频率限制并提高效率。

## 可用工具

### `okx_report`
生成高度压缩的损益（PnL）和状态报告。

### `okx_grid_maintain`
维护网格结构的核心执行工具。

## 内部依赖
需要在 `/root/.openclaw/workspace/okx_data/` 中存在以下本地文件：
- `config.json`: API 凭据。
- `grid_settings.json`: 策略参数。

## ⚠️ 风险提示
加密货币交易涉及巨大风险。本技能按“原样”提供，不作任何保证。
- **模拟优先:** 在使用真实资金之前，务必先开启模拟盘测试 (`OKX_IS_SIMULATION=true`)。
- **权限控制:** 仅使用具备“交易”权限的 API 密钥。**务必禁用“提现”权限。**
