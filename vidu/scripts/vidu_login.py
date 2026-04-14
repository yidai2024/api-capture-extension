#!/usr/bin/env python3
"""
Vidu.cn 登录脚本
使用手机号登录获取更多API接口
"""

import asyncio
import json
from datetime import datetime

from playwright.async_api import async_playwright

class ViduLogin:
    def __init__(self, phone="13711967510"):
        self.phone = phone
        self.api_endpoints = set()
        self.requests_data = []
        
    async def login_and_capture(self):
        print(f"开始登录 vidu.cn，手机号: {self.phone}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()
            
            # 监听请求
            page.on("request", self.handle_request)
            
            # 访问网站
            await page.goto("https://www.vidu.cn/", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # 查找登录按钮
            print("查找登录按钮...")
            login_btn = None
            
            # 尝试多种方式查找登录按钮
            selectors = [
                "text=登录",
                "text=登录/注册",
                "button:has-text('登录')",
                "a:has-text('登录')",
                "[class*='login']",
                "[class*='Login']"
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        login_btn = element
                        print(f"找到登录按钮: {selector}")
                        break
                except:
                    pass
            
            if not login_btn:
                print("未找到登录按钮，尝试截图分析...")
                await page.screenshot(path="/root/vidu_page.png")
                print("页面截图已保存: /root/vidu_page.png")
                await browser.close()
                return
            
            # 点击登录按钮
            await login_btn.click()
            await page.wait_for_timeout(3000)
            
            # 查找手机号输入框
            print("查找手机号输入框...")
            phone_input = None
            
            phone_selectors = [
                "input[type='tel']",
                "input[type='phone']",
                "input[placeholder*='手机']",
                "input[placeholder*='phone']",
                "input[placeholder*='Phone']",
                "input[name*='phone']",
                "input[name*='mobile']"
            ]
            
            for selector in phone_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        phone_input = element
                        print(f"找到手机号输入框: {selector}")
                        break
                except:
                    pass
            
            if not phone_input:
                print("未找到手机号输入框，尝试截图分析...")
                await page.screenshot(path="/root/vidu_login_page.png")
                print("登录页面截图已保存: /root/vidu_login_page.png")
                await browser.close()
                return
            
            # 输入手机号
            print(f"输入手机号: {self.phone}")
            await phone_input.fill(self.phone)
            await page.wait_for_timeout(1000)
            
            # 查找获取验证码按钮
            print("查找获取验证码按钮...")
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
                print("已发送验证码，请查收短信")
                print("=" * 60)
                print("请告诉我收到的验证码，我将完成登录并抓取更多API接口")
                print("=" * 60)
                
                # 截图保存当前状态
                await page.screenshot(path="/root/vidu_captcha_page.png")
                print("验证码页面截图已保存: /root/vidu_captcha_page.png")
            else:
                print("未找到验证码按钮")
                await page.screenshot(path="/root/vidu_no_captcha.png")
                print("页面截图已保存: /root/vidu_no_captcha.png")
            
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
        if resource_type in ["stylesheet", "image", "font"]:
            return False
        
        # 检查URL模式
        api_patterns = ["/api/", "/v1/", "/iam/", "/vidu/", "/service/", ".json"]
        for pattern in api_patterns:
            if pattern in url:
                return True
        
        # XHR/Fetch请求
        if resource_type in ["xhr", "fetch"]:
            return True
        
        return False

async def main():
    login = ViduLogin(phone="13711967510")
    results = await login.login_and_capture()
    
    if results:
        print(f"捕获到 {len(results['captured_apis'])} 个API端点")
        
        # 保存结果
        with open("/root/vidu_login_apis.json", "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
