# Web Scraper - 通用网页爬虫和数据抓取工具

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/openclaw/web-scraper)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Language](https://img.shields.io/badge/language-zh-orange.svg)](https://github.com/openclaw/web-scraper)

## 📋 简介

Web Scraper 是一个功能强大的网页爬虫和数据抓取工具，专为 AI Agent 设计。它能够抓取网页内容、爬取整个网站、搜索网页，并使用 CSS 选择器提取结构化数据。

## ✨ 核心功能

- 🌐 网页内容抓取 (HTML, 文本, 链接)
- 🕵️ 网站爬取 (多页面、多深度)
- 🔍 网页搜索 (Google 搜索)
- 🎯 CSS 选择器数据提取
- 📊 数据导出 (JSON, CSV, TXT)
- 🎭 反爬虫规避 (随机 User-Agent, 延迟)

## 🚀 安装

```bash
pip install requests beautifulsoup4 lxml
```

## 💡 使用示例

### 抓取单个页面
```bash
clawscrape scrape https://example.com
```

### 爬取整个网站
```bash
clawscrape crawl https://example.com --pages 10 --depth 2
```

### 网页搜索
```bash
clawscrape search "OpenClaw AI agent"
```

## 📖 文档

完整文档请参考 [SKILL.md](SKILL.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License
