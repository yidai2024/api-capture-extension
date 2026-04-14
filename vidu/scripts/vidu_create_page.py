#!/usr/bin/env python3
"""
访问Vidu创建视频页面，查找登录入口
"""

import asyncio
import json
from datetime import datetime

from playwright.async_api import async_playwright

class ViduCreatePage:
    def __init__(self, phone="13711967510"):
        self.phone = phone
        self.api_endpoints = set()
        self.requests_data = []
        
    async def visit_create_page(self):
        print(f"访问Vidu创建页面，手机号: {self.phone}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            # 监听请求
            page.on("request", self.handle_request)
            
            # 访问创建页面
            print("访问文本生成视频页面...")
            await page.goto("https://www.vidu.cn/create/text2video", wait_until="networkidle")
            await page.wait_for_timeout(5000)
            
            # 截图
            await page.screenshot(path="/root/vidu_create_page.png")
            print("创建页面截图已保存: /root/vidu_create_page.png")
            
            # 查找登录按钮
            print("查找登录按钮...")
            
            # 尝试多种方式查找
            login_selectors = [
                "text=登录",
                "text=登录/注册",
                "button:has-text('登录')",
                "a:has-text('登录')",
                "[class*='login']",
                "[class*='Login']",
                "text=Sign In",
                "text=Login"
            ]
            
            login_found = False
            for selector in login_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"找到登录元素: {selector}")
                        await element.click()
                        await page.wait_for_timeout(3000)
                        login_found = True
                        break
                except:
                    pass
            
            if not login_found:
                print("未找到登录按钮，尝试其他方法...")
                
                # 尝试查找用户图标
                try:
                    user_icon = await page.query_selector("[class*='user'], [class*='User'], [class*='avatar'], [class*='Avatar']")
                    if user_icon:
                        print("找到用户图标，点击...")
                        await user_icon.click()
                        await page.wait_for_timeout(3000)
                        login_found = True
                except:
                    pass
            
            # 再次截图
            await page.screenshot(path="/root/vidu_after_login_click.png")
            print("点击后截图已保存: /root/vidu_after_login_click.png")
            
            # 查找手机号输入框
            print("查找手机号输入框...")
            
            # 等待可能的登录模态框
            await page.wait_for_timeout(2000)
            
            # 查找输入框
            phone_selectors = [
                "input[type='tel']",
                "input[type='phone']",
                "input[placeholder*='手机']",
                "input[placeholder*='phone']",
                "input[placeholder*='Phone']",
                "input[name*='phone']",
                "input[name*='mobile']"
            ]
            
            phone_input = None
            for selector in phone_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        phone_input = element
                        print(f"找到手机号输入框: {selector}")
                        break
                except:
                    pass
            
            if phone_input:
                print(f"输入手机号: {self.phone}")
                await phone_input.fill(self.phone)
                await page.wait_for_timeout(1000)
                
                # 查找验证码按钮
                captcha_btn = None
                captcha_selectors = [
                    "button:has-text('验证码')",
                    "button:has-text('获取')",
                    "button:has-text('发送')",
                    "text=获取验证码",
                    "text=发送验证码"
                ]
                
                for selector in captcha_selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            captcha_btn = element
                            print(f"找到验证码按钮: {selector}")
                            break
                    except:
                        pass
                
                if captcha_btn:
                    await captcha_btn.click()
                    await page.wait_for_timeout(2000)
                    print("已发送验证码！")
                    print("=" * 60)
                    print("请告诉我收到的验证码，我将完成登录")
                    print("=" * 60)
                    
                    # 截图保存
                    await page.screenshot(path="/root/vidu_captcha_page.png")
                    print("验证码页面截图已保存: /root/vidu_captcha_page.png")
                else:
                    print("未找到验证码按钮")
            else:
                print("未找到手机号输入框")
            
            # 分析页面内容
            print("\n分析页面内容...")
            content = await page.content()
            
            # 查找API相关代码
            import re
            api_patterns = [
                r'service\.vidu\.cn/[^"\']+',
                r'api/[^"\']+',
                r'/v1/[^"\']+',
                r'iam/[^"\']+',
                r'credit/[^"\']+',
                r'vidu/[^"\']+',
            ]
            
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if "http" in match:
                        self.api_endpoints.add(match)
                    else:
                        self.api_endpoints.add(f"https://service.vidu.cn/{match}")
            
            print(f"从页面内容中发现 {len(self.api_endpoints)} 个API端点")
            
            await browser.close()
            
        return {
            "captured_apis": list(self.api_endpoints),
            "total_requests": len(self.requests_data)
        }
    
    def handle_request(self, request):
        url = request.url
        method = request.method
        
        self.requests_data.append({
            "url": url,
            "method": method,
            "type": request.resource_type
        })
        
        # 记录API请求
        if self.is_api(url, request.resource_type):
            self.api_endpoints.add(url)
            print(f"API: {method} {url}")
    
    def is_api(self, url, resource_type):
        # 排除静态资源
        if resource_type in ["stylesheet", "image", "font", "media"]:
            return False
        
        # 检查URL模式
        api_patterns = ["/api/", "/v1/", "/iam/", "/vidu/", "/service/", "/credit/", ".json"]
        for pattern in api_patterns:
            if pattern in url:
                return True
        
        # XHR/Fetch请求
        if resource_type in ["xhr", "fetch"]:
            return True
        
        return False

async def main():
    create_page = ViduCreatePage(phone="13711967510")
    results = await create_page.visit_create_page()
    
    if results:
        print(f"\n总共捕获到 {len(results['captured_apis'])} 个API端点")
        
        # 保存结果
        with open("/root/vidu_create_page_apis.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # 显示新发现的API
        print("\n新发现的API端点:")
        for api in sorted(results['captured_apis']):
            print(f"  - {api}")

if __name__ == "__main__":
    asyncio.run(main())
