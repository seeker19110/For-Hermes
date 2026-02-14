# NOFX 常见问题 (FAQ)

## 安装部署

### Q: 安装失败怎么办？

**检查清单：**
1. Docker 是否已安装并运行？
2. 端口 3000 是否被占用？
3. 网络是否能访问 GitHub？

**解决方案：**
```bash
# 检查 Docker
docker --version

# 检查端口
lsof -i :3000

# 手动拉取镜像
docker pull nofxai/nofx:latest
```

### Q: 如何更新到最新版？

```bash
# 重新运行安装脚本
curl -fsSL https://raw.githubusercontent.com/NoFxAiOS/nofx/main/install.sh | bash
```

### Q: 数据会丢失吗？

不会。数据存储在 Docker volume 中，更新不影响数据。

---

## API 问题

### Q: API 返回 403 Forbidden？

**原因：**
1. API Key 无效或过期
2. 请求频率超限 (>30/s)
3. IP 被临时封禁

**解决：**
1. 检查 API Key 是否正确
2. 降低请求频率
3. 等待几分钟后重试

### Q: API Key 从哪里获取？

访问 https://nofxos.ai/api-docs 页面顶部显示。

### Q: API 请求超时？

1. 检查网络连接
2. 使用代理（如有必要）
3. 增加超时时间

---

## 交易所配置

### Q: API Key 配置后报错？

**检查：**
1. API Key 和 Secret 是否复制完整
2. 权限是否开启（读取+交易）
3. IP 白名单是否配置
4. OKX 需要额外的 Passphrase

### Q: 为什么提示 "Insufficient Balance"？

1. 账户余额不足
2. 保证金不足
3. 仓位超限

### Q: 支持模拟交易吗？

部分交易所支持：
- Binance: 需要申请测试网 API
- Bybit: 支持模拟交易模式
- OKX: 支持模拟交易

---

## 策略问题

### Q: 策略不触发交易？

**检查：**
1. Trader 是否已启动？
2. 策略是否已激活？
3. 市场条件是否满足？
4. 查看 AI 决策日志

### Q: 如何优化策略？

1. 回测不同参数
2. 分析历史交易
3. 调整风控参数
4. 参考 AI 建议

### Q: 策略亏损怎么办？

1. 检查策略逻辑
2. 分析亏损原因
3. 降低仓位/杠杆
4. 考虑暂停交易

---

## Trader 问题

### Q: Trader 启动失败？

**常见原因：**
1. 交易所 API 配置错误
2. AI 模型 API Key 无效
3. 策略配置问题

**排查步骤：**
1. 检查 Trader 日志
2. 验证交易所连接
3. 测试 AI 模型响应

### Q: Trader 不下单？

1. 检查账户余额
2. 查看 AI 决策日志
3. 确认市场条件
4. 检查风控限制

### Q: 如何查看 Trader 日志？

Dashboard → 选择 Trader → 查看 AI Decision Logs

---

## 网格交易

### Q: 网格利润不理想？

1. 检查价格区间设置
2. 调整网格数量
3. 考虑市场是否适合网格

### Q: 价格突破边界怎么办？

1. 系统自动止损（如已配置）
2. 手动调整边界
3. 考虑暂停网格

### Q: 网格和 AI 策略冲突吗？

不冲突。可以同时运行：
- 网格策略做震荡
- AI 策略做趋势

---

## 安全问题

### Q: 资金安全吗？

1. NOFX 不托管资金
2. 资金始终在交易所
3. 建议关闭提现权限
4. 使用 IP 白名单

### Q: 如何保护 API Key？

1. 不要分享 API Key
2. 开启 IP 白名单
3. 定期更换 Key
4. 使用子账户

### Q: 发现异常交易？

1. 立即停止 Trader
2. 检查交易所账户
3. 更换 API Key
4. 检查服务器安全

---

## 性能问题

### Q: 系统很卡？

1. 检查服务器资源
2. 减少同时运行的 Trader
3. 清理历史日志
4. 考虑升级配置

**建议配置：**
- CPU: 2 核+
- 内存: 4GB+
- 存储: 20GB+

### Q: 延迟很高？

1. 选择离交易所近的服务器
2. 使用低延迟网络
3. 减少不必要的数据请求

---

## 其他问题

### Q: 如何加入社区？

- Telegram: https://t.me/nofx_dev_community
- Twitter: https://x.com/nofx_official
- GitHub: https://github.com/NoFxAiOS/nofx

### Q: 如何反馈 Bug？

GitHub Issues: https://github.com/NoFxAiOS/nofx/issues

### Q: 有教程视频吗？

查看官方 Twitter 和 Telegram 群的置顶消息。

### Q: 收费吗？

NOFX 完全开源免费。
- 交易所手续费自理
- AI API 费用自理
- 服务器费用自理
