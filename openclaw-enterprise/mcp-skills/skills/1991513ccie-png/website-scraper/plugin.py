#!/usr/bin/env python3
"""
Web Scraper Plugin
通用网页爬虫和数据抓取工具
"""

import os
import sys
import json
import argparse
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urljoin, urlparse
from pathlib import Path
import csv
from bs4 import BeautifulSoup
import re


class WebScraper:
    """Web Scraper - 通用网页爬虫和数据抓取工具"""
    
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.session = requests.Session()
        self.session.headers.update(self.config['headers'])
        self.visited_urls = set()
        self.data = []
        
    def _default_config(self) -> Dict:
        return {
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            },
            'timeout': 30,
            'delay': 1,
            'max_pages': 100,
            'max_depth': 3,
            'user_agents': [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            ],
            'proxies': [],
            'output_dir': '~/.clawhub/scraping',
            'extract_links': True,
            'extract_texts': True,
            'extract_images': False,
            'extract_tables': False,
        }
    
    def _random_delay(self):
        """随机延迟，模拟人类行为"""
        delay = self.config.get('delay', 1)
        time.sleep(delay + random.uniform(0, 0.5))
    
    def _get_random_user_agent(self) -> str:
        """随机 User-Agent"""
        return random.choice(self.config.get('user_agents', [self.config['headers']['User-Agent']]))
    
    def fetch_page(self, url: str) -> Optional[requests.Response]:
        """获取网页内容"""
        try:
            self._random_delay()
            headers = {'User-Agent': self._get_random_user_agent()}
            response = self.session.get(url, headers=headers, timeout=self.config['timeout'])
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_html(self, html: str, url: str) -> Dict:
        """解析 HTML 内容"""
        soup = BeautifulSoup(html, 'html.parser')
        
        result = {
            'url': url,
            'title': soup.title.string if soup.title else '',
            'links': [],
            'texts': [],
            'images': [],
            'tables': [],
        }
        
        if self.config.get('extract_links'):
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(url, href)
                result['links'].append({
                    'url': absolute_url,
                    'text': link.get_text(strip=True),
                    'title': link.get('title', '')
                })
        
        if self.config.get('extract_texts'):
            # Extract main content
            for element in soup.find_all(['p', 'h1', 'h2', 'h3', 'li', 'span', 'div']):
                text = element.get_text(strip=True)
                if text and len(text) > 10:  # Filter out short text
                    result['texts'].append(text)
        
        if self.config.get('extract_images'):
            for img in soup.find_all('img', src=True):
                src = img.get('src', '')
                alt = img.get('alt', '')
                absolute_url = urljoin(url, src)
                result['images'].append({
                    'url': absolute_url,
                    'alt': alt
                })
        
        if self.config.get('extract_tables'):
            for table in soup.find_all('table'):
                table_data = []
                headers = []
                rows = table.find_all('tr')
                for i, row in enumerate(rows):
                    cells = row.find_all(['td', 'th'])
                    if i == 0:
                        headers = [cell.get_text(strip=True) for cell in cells]
                    else:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        table_data.append(row_data)
                result['tables'].append({
                    'headers': headers,
                    'data': table_data
                })
        
        return result
    
    def scrape_page(self, url: str) -> Optional[Dict]:
        """抓取单个页面"""
        response = self.fetch_page(url)
        if not response:
            return None
        
        result = self.parse_html(response.text, url)
        result['status_code'] = response.status_code
        result['fetched_at'] = datetime.now().isoformat()
        
        return result
    
    def scrape_multiple_pages(self, urls: List[str]) -> List[Dict]:
        """抓取多个页面"""
        results = []
        for url in urls:
            result = self.scrape_page(url)
            if result:
                results.append(result)
        return results
    
    def crawl(self, start_url: str, max_pages: int = None, max_depth: int = None) -> List[Dict]:
        """爬取网站"""
        max_pages = max_pages or self.config.get('max_pages', 100)
        max_depth = max_depth or self.config.get('max_depth', 3)
        
        results = []
        queue = [(start_url, 0)]
        visited = set()
        
        while queue and len(visited) < max_pages:
            url, depth = queue.pop(0)
            
            if url in visited or depth > max_depth:
                continue
            
            visited.add(url)
            result = self.scrape_page(url)
            
            if result:
                result['depth'] = depth
                results.append(result)
                
                # Add discovered links to queue
                for link in result.get('links', [])[:10]:  # Limit to 10 links per page
                    link_url = link['url']
                    if link_url not in visited and link_url.startswith(urlparse(start_url).scheme + '://'):
                        queue.append((link_url, depth + 1))
        
        return results
    
    def extract_data(self, html: str, selectors: Dict[str, str]) -> Dict:
        """使用 CSS 选择器提取数据"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        for key, selector in selectors.items():
            elements = soup.select(selector)
            if elements:
                if len(elements) == 1:
                    result[key] = elements[0].get_text(strip=True)
                else:
                    result[key] = [el.get_text(strip=True) for el in elements]
            else:
                result[key] = None
        
        return result
    
    def search(self, query: str, search_engine: str = 'google') -> List[Dict]:
        """搜索网页"""
        if search_engine == 'google':
            url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
            response = self.fetch_page(url)
            
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                for item in soup.select('.g')[:10]:  # First 10 results
                    title_elem = item.select_one('h3')
                    link_elem = item.select_one('a')
                    desc_elem = item.select_one('.VwiC3b')
                    
                    if title_elem and link_elem:
                        results.append({
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'description': desc_elem.get_text(strip=True) if desc_elem else ''
                        })
                
                return results
        
        return []
    
    def save_data(self, data: List[Dict], filename: str = None, format: str = 'json'):
        """保存数据"""
        output_dir = Path(self.config['output_dir']).expanduser()
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not filename:
            filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}"
        
        filepath = output_dir / filename
        
        if format == 'json':
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == 'csv':
            if data:
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        
        elif format == 'txt':
            with open(filepath, 'w', encoding='utf-8') as f:
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        return str(filepath)
    
    def clean_html(self, html: str) -> str:
        """清理 HTML，移除脚本和样式"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(['script', 'style']):
            script.decompose()
        
        return soup.get_text(separator=' ', strip=True)


def scrape_command(args):
    """Command: scrape a single page"""
    scraper = WebScraper()
    
    if args.url:
        result = scraper.scrape_page(args.url)
        if result:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print("Failed to scrape the page")
    else:
        print("Error: URL is required")
        sys.exit(1)


def crawl_command(args):
    """Command: crawl a website"""
    scraper = WebScraper()
    
    if args.url:
        results = scraper.crawl(
            args.url,
            max_pages=args.pages,
            max_depth=args.depth
        )
        
        if results:
            if args.output:
                filepath = scraper.save_data(results, args.output, args.format)
                print(f"Saved {len(results)} pages to {filepath}")
            else:
                print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print("No pages scraped")
    else:
        print("Error: URL is required")
        sys.exit(1)


def search_command(args):
    """Command: search the web"""
    scraper = WebScraper()
    
    if args.query:
        results = scraper.search(args.query)
        
        if results:
            if args.output:
                filepath = scraper.save_data(results, args.output, args.format)
                print(f"Saved {len(results)} results to {filepath}")
            else:
                print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            print("No results found")
    else:
        print("Error: Query is required")
        sys.exit(1)


def extract_command(args):
    """Command: extract data using CSS selectors"""
    scraper = WebScraper()
    
    if args.html_file:
        with open(args.html_file, 'r', encoding='utf-8') as f:
            html = f.read()
        
        selectors = {}
        if args.selectors:
            for selector in args.selectors:
                if '=' in selector:
                    key, selector_str = selector.split('=', 1)
                    selectors[key] = selector_str
        
        result = scraper.extract_data(html, selectors)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Error: HTML file is required")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Web Scraper - 通用网页爬虫和数据抓取工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  clawscrape scrape https://example.com
  clawscrape crawl https://example.com --pages 10 --depth 2
  clawscrape search "OpenClaw AI agent" --output results.json
  clawscrape extract page.html --selector="title=h1" --selector="content=.main"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape a single page')
    scrape_parser.add_argument('url', help='URL to scrape')
    scrape_parser.add_argument('--output', '-o', help='Output file')
    scrape_parser.add_argument('--format', '-f', default='json', choices=['json', 'csv', 'txt'], help='Output format')
    
    # Crawl command
    crawl_parser = subparsers.add_parser('crawl', help='Crawl a website')
    crawl_parser.add_argument('url', help='Starting URL')
    crawl_parser.add_argument('--pages', '-p', type=int, default=10, help='Max pages to crawl')
    crawl_parser.add_argument('--depth', '-d', type=int, default=3, help='Max crawl depth')
    crawl_parser.add_argument('--output', '-o', help='Output file')
    crawl_parser.add_argument('--format', '-f', default='json', choices=['json', 'csv', 'txt'], help='Output format')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search the web')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--engine', '-e', default='google', choices=['google'], help='Search engine')
    search_parser.add_argument('--output', '-o', help='Output file')
    search_parser.add_argument('--format', '-f', default='json', choices=['json', 'csv', 'txt'], help='Output format')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract data using CSS selectors')
    extract_parser.add_argument('html_file', help='HTML file to extract from')
    extract_parser.add_argument('--selector', '-s', action='append', help='CSS selector in format key=selector')
    extract_parser.add_argument('--output', '-o', help='Output file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    if args.command == 'scrape':
        scrape_command(args)
    elif args.command == 'crawl':
        crawl_command(args)
    elif args.command == 'search':
        search_command(args)
    elif args.command == 'extract':
        extract_command(args)


if __name__ == '__main__':
    main()
