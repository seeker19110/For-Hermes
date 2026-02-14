# SKILL.md - Web Scraper Skill

# Web Scraper - 通用网页爬虫和数据抓取工具

## 简介
Web Scraper 是一个功能强大的网页爬虫和数据抓取工具，专为 AI Agent 设计。它能够抓取网页内容、爬取整个网站、搜索网页，并使用 CSS 选择器提取结构化数据。

## 核心能力
- 🌐 网页内容抓取 (HTML, 文本, 链接)
- 🕵️ 网站爬取 (多页面、多深度)
- 🔍 网页搜索 (Google 搜索)
- 🎯 CSS 选择器数据提取
- 📊 数据导出 (JSON, CSV, TXT)
- 🎭 反爬虫规避 (随机 User-Agent, 延迟)

## 使用场景
- 网页内容抓取
- 网站数据爬取
- 搜索引擎结果获取
- 数据清洗和转换
- 市场调研和竞争分析
- 内容监控和通知

## API 端点

### 抓取单个页面
```bash
clawscrape scrape <url> [options]
```

### 爬取整个网站
```bash
clawscrape crawl <url> [options]
```

### 网页搜索
```bash
clawscrape search <query> [options]
```

### CSS 选择器提取
```bash
clawscrape extract <html_file> [options]
```

## 安装依赖
```bash
pip install requests beautifulsoup4 lxml
```

## 示例用法

### 1. 抓取单个页面
```bash
# 抓取单个页面
clawscrape scrape https://example.com

# 抓取并保存为 JSON
clawscrape scrape https://example.com --output data.json

# 抓取并保存为 CSV
clawscrape scrape https://example.com --output data.csv --format csv
```

### 2. 爬取整个网站
```bash
# 爬取网站 (默认 10 页，深度 3)
clawscrape crawl https://example.com

# 爬取更多页面
clawscrape crawl https://example.com --pages 50 --depth 5

# 爬取并保存
clawscrape crawl https://example.com --output site_data.json
```

### 3. 网页搜索
```bash
# 搜索网页
clawscrape search "OpenClaw AI agent"

# 搜索并保存结果
clawscrape search "OpenClaw AI agent" --output results.json
```

### 4. CSS 选择器提取
```bash
# 使用 CSS 选择器提取数据
clawscrape extract page.html --selector="title=h1" --selector="content=.main"

# 多个选择器
clawscrape extract article.html \
  --selector="title=h1" \
  --selector="author=.author" \
  --selector="date=.date" \
  --selector="content=.body"
```

## 支持的功能

### 抓取功能
- ✅ HTML 内容抓取
- ✅ 文本提取
- ✅ 链接提取
- ✅ 图片提取
- ✅ 表格提取
- ✅ 响应状态码检查
- ✅ 错误处理和重试

### 爬取功能
- ✅ 多页面爬取
- ✅ 深度限制
- ✅ 链接发现和跟随
- ✅ URL 规范化
- ✅ 重复 URL 过滤

### 搜索功能
- ✅ Google 搜索
- ✅ 结果提取
- ✅ 分页支持
- ✅ 搜索限制

### 数据提取
- ✅ CSS 选择器
- ✅ 属性提取
- ✅ 文本提取
- ✅ 多元素支持

### 输出格式
- ✅ JSON
- ✅ CSV
- ✅ TXT
- ✅ 文件自动保存

## 命令行工具

### clawscrape 命令
```bash
clawscrape [options] <command> [args]

Commands:
  scrape      抓取单个页面
  crawl       爬取整个网站
  search      网页搜索
  extract     CSS 选择器提取

Options:
  --help      显示帮助
  --version   显示版本
  --verbose   详细输出
  --quiet     安静模式
```

## 配置选项
```json
{
  "headers": {
    "User-Agent": "Mozilla/5.0...",
    "Accept": "text/html..."
  },
  "timeout": 30,
  "delay": 1,
  "max_pages": 100,
  "max_depth": 3,
  "user_agents": [...],
  "proxies": [],
  "output_dir": "~/.clawhub/scraping"
}
```

## Python API
```python
from web_scraper import WebScraper

# 初始化
scraper = WebScraper()

# 抓取页面
result = scraper.scrape_page('https://example.com')
print(result['title'])
print(result['links'])
print(result['texts'])

# 爬取网站
results = scraper.crawl('https://example.com', max_pages=10, max_depth=3)

# 搜索
results = scraper.search('OpenClaw AI agent')

# 提取数据
selectors = {
    'title': 'h1',
    'content': '.main-content'
}
data = scraper.extract_data(html, selectors)

# 保存数据
filepath = scraper.save_data([result], 'output.json')
```

## 最佳实践
1. always add delay between requests to avoid rate limiting
2. use appropriate User-Agent strings
3. respect robots.txt and website terms
4. handle errors gracefully
5. save data regularly
6. limit crawl depth to avoid excessive requests
7. use CSS selectors for precise data extraction
8. validate extracted data before processing

## 未来功能
- 🚀 JavaScript 渲染支持 (Playwright/Selenium)
- 🚀 API 端点爬取
- 🚀 分布式爬取
- 🚀 代理池支持
- 🚀 反爬虫绕过 (Cloudflare, Captcha)
- 🚀 实时数据流
- 🚀 数据增量更新

## 许可证
MIT License

## 贡献
欢迎提交 Issue 和 Pull Request!

## 联系方式
- GitHub: https://github.com/openclaw/web-scraper
- Discord: #clawhub-scraping channel
