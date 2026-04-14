#!/usr/bin/env python3
"""
Vidu.cn API接口抓取工具
用于抓取网站的所有API接口
"""

import asyncio
import json
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright未安装，尝试安装...")

class ViduApiScraper:
    def __init__(self):
        self.api_endpoints = set()
        self.js_files = set()
        self.network_requests = []
        self.visited_urls = set()
        
    async def install_playwright(self):
        """安装Playwright"""
        import subprocess
        print("正在安装Playwright...")
        subprocess.run(["pip", "install", "playwright"], check=True)
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("Playwright安装完成")
        
    async def scrape_apis(self, url="https://www.vidu.cn/"):
        """抓取API接口"""
        if not PLAYWRIGHT_AVAILABLE:
            await self.install_playwright()
            from playwright.async_api import async_playwright
            
        print(f"开始抓取 {url} 的API接口...")
        print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # 监听网络请求
            page.on("request", self._on_request)
            page.on("response", self._on_response)
            
            # 访问主页
            print(f"访问主页: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待页面加载
            await page.wait_for_timeout(3000)
            
            # 滚动页面触发懒加载
            await self._scroll_page(page)
            
            # 点击页面上的按钮/链接
            await self._click_elements(page)
            
            # 查找登录按钮
            await self._find_login(page)
            
            # 分析JavaScript文件
            await self._analyze_js_files(page)
            
            await browser.close()
            
        print(f"抓取完成!")
        print(f"发现API端点: {len(self.api_endpoints)}个")
        print(f"JS文件: {len(self.js_files)}个")
        print(f"网络请求: {len(self.network_requests)}个")
        
        return {
            "api_endpoints": list(self.api_endpoints),
            "js_files": list(self.js_files),
            "network_requests": self.network_requests
        }
    
    def _on_request(self, request):
        """处理请求事件"""
        url = request.url
        method = request.method
        
        # 记录网络请求
        request_data = {
            "url": url,
            "method": method,
            "resource_type": request.resource_type,
            "headers": dict(request.headers),
            "timestamp": datetime.now().isoformat()
        }
        
        # 如果是API请求
        if self._is_api_request(url, request.resource_type):
            self.api_endpoints.add(url)
            request_data["is_api"] = True
            print(f"  发现API: {method} {url}")
        
        # 如果是JS文件
        if url.endswith('.js') or 'javascript' in request.resource_type:
            self.js_files.add(url)
        
        self.network_requests.append(request_data)
    
    def _on_response(self, response):
        """处理响应事件"""
        url = response.url
        status = response.status
        
        # 更新网络请求状态
        for req in self.network_requests:
            if req["url"] == url:
                req["status"] = status
                break
    
    def _is_api_request(self, url, resource_type):
        """判断是否为API请求"""
        # 排除静态资源
        if resource_type in ["stylesheet", "image", "font", "media"]:
            return False
        
        # 排除常见静态文件
        static_extensions = ['.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', 
                            '.ico', '.woff', '.woff2', '.ttf', '.eot', '.mp4', '.webm']
        if any(url.endswith(ext) for ext in static_extensions):
            return False
        
        # 检查URL特征
        api_patterns = [
            r'/api/',
            r'/v[0-9]+/',
            r'/graphql',
            r'/rest/',
            r'/service/',
            r'\.json',
            r'/ajax/',
            r'/rpc/',
        ]
        
        for pattern in api_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # 检查是否为XHR/Fetch请求
        if resource_type in ["xhr", "fetch"]:
            return True
        
        return False
    
    async def _scroll_page(self, page):
        """滚动页面触发懒加载"""
        print("  滚动页面触发懒加载...")
        for i in range(5):
            await page.evaluate(f"window.scrollTo(0, {(i+1) * 500})")
            await page.wait_for_timeout(1000)
    
    async def _click_elements(self, page):
        """点击页面元素触发更多请求"""
        print("  点击页面元素...")
        
        # 查找可点击元素
        clickables = await page.query_selector_all("a, button, [onclick], [role='button']")
        
        # 只点击前5个避免过多请求
        for i, element in enumerate(clickables[:5]):
            try:
                text = await element.inner_text()
                href = await element.get_attribute("href")
                
                if text or href:
                    print(f"    点击元素: {text[:30] if text else href[:30]}...")
                    await element.click()
                    await page.wait_for_timeout(1000)
            except Exception as e:
                pass
    
    async def _find_login(self, page):
        """查找登录功能"""
        print("  查找登录功能...")
        
        # 查找登录相关元素
        login_patterns = ["登录", "login", "sign in", "signin", "注册", "register"]
        
        for pattern in login_patterns:
            try:
                element = await page.query_selector(f"text=/{pattern}/i")
                if element:
                    print(f"    找到登录元素: {pattern}")
                    await element.click()
                    await page.wait_for_timeout(2000)
                    break
            except:
                pass
    
    async def _analyze_js_files(self, page):
        """分析JavaScript文件中的API"""
        print("  分析JavaScript文件...")
        
        # 获取页面中的script标签
        scripts = await page.query_selector_all("script[src]")
        
        for script in scripts:
            src = await script.get_attribute("src")
            if src:
                self.js_files.add(src)
        
        # 获取页面源代码中的API
        content = await page.content()
        
        # 查找API模式
        api_patterns = [
            r'["'](https?://[^"']*(?:api|v[0-9]+|graphql|rest|service)[^"']*)["']',
            r'["'](/[^"']*(?:api|v[0-9]+|graphql|rest|service)[^"']*)["']',
            r'fetch\s*\(\s*["']([^"']+)["']',
            r'axios\s*\.\s*(?:get|post|put|delete)\s*\(\s*["']([^"']+)["']',
            r'\$\.ajax\s*\(\s*\{\s*url\s*:\s*["']([^"']+)["']',
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match and not match.startswith("data:"):
                    self.api_endpoints.add(match)
                    print(f"    从JS中发现API: {match}")

async def main():
    scraper = ViduApiScraper()
    results = await scraper.scrape_apis()
    
    # 保存结果
    with open("/root/vidu_api_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # 生成报告
    report = f"""
========================================
Vidu.cn API接口抓取报告
========================================
抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

统计信息:
- 发现API端点: {len(results['api_endpoints'])}个
- 发现JS文件: {len(results['js_files'])}个
- 总网络请求: {len(results['network_requests'])}个

API端点列表:
{chr(10).join(f'  {i+1}. {api}' for i, api in enumerate(results['api_endpoints']))}

JS文件列表:
{chr(10).join(f'  {i+1}. {js}' for i, js in enumerate(results['js_files']))}
========================================
"""
    
    with open("/root/vidu_api_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
