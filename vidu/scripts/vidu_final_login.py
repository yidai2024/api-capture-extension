#!/usr/bin/env python3
"""
Vidu.cn 最终登录脚本
获取验证码并等待用户输入
"""

import asyncio
import json
from datetime import datetime

from playwright.async_api import async_playwright

class ViduFinalLogin:
    def __init__(self, phone="13711967510"):
        self.phone = phone
        self.api_endpoints = set()
        self.requests_data = []
        
    async def get_captcha(self):
        print(f"获取验证码，手机号: {self.phone}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            # 监听请求
            page.on("request", self.handle_request)
            
            # 访问创建页面
            print("访问创建页面...")
            await page.goto("https://www.vidu.cn/create/text2video", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # 点击登录按钮
            print("点击登录按钮...")
            try:
                await page.click("text=登录", timeout=5000)
                await page.wait_for_timeout(3000)
                print("成功打开登录弹窗")
            except Exception as e:
                print(f"点击登录按钮失败: {e}")
                await browser.close()
                return False
            
            # 查找手机号输入框
            print("查找手机号输入框...")
            try:
                phone_input = await page.query_selector("input[placeholder*='手机']")
                if phone_input:
                    print(f"找到手机号输入框，输入: {self.phone}")
                    await phone_input.fill(self.phone)
                    await page.wait_for_timeout(1000)
                    
                    # 使用JavaScript点击按钮绕过遮罩层
                    print("使用JavaScript点击'获取/登录'按钮...")
                    try:
                        # 使用evaluate执行JavaScript点击
                        await page.evaluate("""
                            // 查找包含"获取"或"登录"文字的按钮
                            const buttons = document.querySelectorAll('button');
                            for (const btn of buttons) {
                                if (btn.textContent.includes('获取') || btn.textContent.includes('登录')) {
                                    console.log('找到按钮:', btn.textContent);
                                    btn.click();
                                    break;
                                }
                            }
                        """)
                        await page.wait_for_timeout(3000)
                        print("已发送验证码！")
                        
                        # 截图保存
                        await page.screenshot(path="/root/vidu_captcha_sent_final.png")
                        print("验证码发送成功截图已保存: /root/vidu_captcha_sent_final.png")
                        
                        return True
                        
                    except Exception as e:
                        print(f"JavaScript点击失败: {e}")
                        return False
                else:
                    print("未找到手机号输入框")
                    return False
            except Exception as e:
                print(f"查找输入框失败: {e}")
                return False
            
            await browser.close()
    
    async def login_with_captcha(self, captcha):
        print(f"使用验证码登录: {captcha}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            # 监听请求
            page.on("request", self.handle_request)
            
            # 访问创建页面
            print("访问创建页面...")
            await page.goto("https://www.vidu.cn/create/text2video", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            # 点击登录按钮
            print("点击登录按钮...")
            try:
                await page.click("text=登录", timeout=5000)
                await page.wait_for_timeout(3000)
                print("成功打开登录弹窗")
            except Exception as e:
                print(f"点击登录按钮失败: {e}")
                await browser.close()
                return
            
            # 查找手机号输入框
            print("查找手机号输入框...")
            try:
                phone_input = await page.query_selector("input[placeholder*='手机']")
                if phone_input:
                    print(f"找到手机号输入框，输入: {self.phone}")
                    await phone_input.fill(self.phone)
                    await page.wait_for_timeout(1000)
                    
                    # 查找验证码输入框
                    print("查找验证码输入框...")
                    captcha_input = await page.query_selector("input[placeholder*='验证码']")
                    if captcha_input:
                        print(f"找到验证码输入框，输入: {captcha}")
                        await captcha_input.fill(captcha)
                        await page.wait_for_timeout(1000)
                        
                        # 使用JavaScript点击登录按钮
                        print("使用JavaScript点击登录按钮...")
                        await page.evaluate("""
                            // 查找包含"登录"文字的按钮
                            const buttons = document.querySelectorAll('button');
                            for (const btn of buttons) {
                                if (btn.textContent.includes('登录')) {
                                    console.log('找到登录按钮:', btn.textContent);
                                    btn.click();
                                    break;
                                }
                            }
                        """)
                        await page.wait_for_timeout(5000)
                        
                        # 截图保存
                        await page.screenshot(path="/root/vidu_login_success.png")
                        print("登录完成截图已保存: /root/vidu_login_success.png")
                        
                        # 等待页面跳转
                        await page.wait_for_timeout(3000)
                        
                        # 继续抓取API
                        print("继续抓取登录后的API...")
                        await self.capture_logged_in_apis(page)
                        
                    else:
                        print("未找到验证码输入框")
                else:
                    print("未找到手机号输入框")
            except Exception as e:
                print(f"登录失败: {e}")
            
            await browser.close()
    
    async def capture_logged_in_apis(self, page):
        """抓取登录后的API"""
        print("开始抓取登录后的API...")
        
        # 访问多个页面抓取API
        pages_to_visit = [
            "https://www.vidu.cn/create/text2video",
            "https://www.vidu.cn/create/img2video",
            "https://www.vidu.cn/create/character2video",
            "https://www.vidu.cn/templates",
            "https://www.vidu.cn/pricing"
        ]
        
        for url in pages_to_visit:
            print(f"访问: {url}")
            try:
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(3000)
                
                # 滚动页面
                for i in range(3):
                    await page.evaluate(f"window.scrollBy(0, 500)")
                    await page.wait_for_timeout(1000)
                    
            except Exception as e:
                print(f"访问 {url} 失败: {e}")
        
        print(f"抓取完成，共发现 {len(self.api_endpoints)} 个API端点")
    
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
        api_patterns = ["/api/", "/v1/", "/iam/", "/vidu/", "/service/", "/credit/", "/tasks/", ".json"]
        for pattern in api_patterns:
            if pattern in url:
                return True
        
        # XHR/Fetch请求
        if resource_type in ["xhr", "fetch"]:
            return True
        
        return False

async def main():
    login = ViduFinalLogin(phone="13711967510")
    
    # 获取验证码
    success = await login.get_captcha()
    
    if success:
        print("=" * 60)
        print("验证码已发送！请查看你的手机短信")
        print("然后告诉我验证码，我将完成登录并抓取更多API")
        print("=" * 60)
    else:
        print("获取验证码失败")

if __name__ == "__main__":
    asyncio.run(main())
