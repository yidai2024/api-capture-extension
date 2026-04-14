#!/usr/bin/env python3
"""
Vidu.cn 正确发送验证码脚本
"""

import asyncio
import json
from datetime import datetime

from playwright.async_api import async_playwright

class ViduCaptchaSender:
    def __init__(self, phone="13711967510"):
        self.phone = phone
        self.api_endpoints = set()
        
    async def send_captcha(self):
        print(f"正确发送验证码，手机号: {self.phone}")
        
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
                    
                    # 先同意用户协议（如果需要）
                    print("检查是否需要同意用户协议...")
                    try:
                        # 查找复选框或同意按钮
                        checkbox = await page.query_selector("input[type='checkbox']")
                        if checkbox:
                            print("找到用户协议复选框，点击同意...")
                            await checkbox.click()
                            await page.wait_for_timeout(1000)
                    except:
                        pass
                    
                    # 查找真正的"获取验证码"按钮
                    print("查找'获取验证码'按钮...")
                    
                    # 尝试多种方式查找按钮
                    button_found = False
                    
                    # 方法1: 查找包含"获取"文字的按钮
                    try:
                        get_code_btn = await page.query_selector("button:has-text('获取')")
                        if get_code_btn:
                            print("找到'获取'按钮，点击...")
                            await get_code_btn.click()
                            button_found = True
                    except:
                        pass
                    
                    # 方法2: 查找包含"发送"文字的按钮
                    if not button_found:
                        try:
                            send_btn = await page.query_selector("button:has-text('发送')")
                            if send_btn:
                                print("找到'发送'按钮，点击...")
                                await send_btn.click()
                                button_found = True
                        except:
                            pass
                    
                    # 方法3: 使用JavaScript查找所有按钮并分析
                    if not button_found:
                        print("使用JavaScript分析所有按钮...")
                        buttons_info = await page.evaluate("""
                            const buttons = document.querySelectorAll('button');
                            const info = [];
                            buttons.forEach((btn, index) => {
                                info.push({
                                    index: index,
                                    text: btn.textContent.trim(),
                                    className: btn.className,
                                    disabled: btn.disabled,
                                    type: btn.type
                                });
                            });
                            return info;
                        """)
                        
                        print(f"找到 {len(buttons_info)} 个按钮:")
                        for btn_info in buttons_info:
                            print(f"  按钮 {btn_info['index']}: '{btn_info['text']}' (类型: {btn_info['type']}, 禁用: {btn_info['disabled']})")
                            
                            # 查找可能是验证码按钮的
                            if '获取' in btn_info['text'] or '验证码' in btn_info['text']:
                                print(f"  -> 可能是验证码按钮，尝试点击...")
                                await page.evaluate(f"""
                                    const buttons = document.querySelectorAll('button');
                                    if (buttons[{btn_info['index']}]) {{
                                        buttons[{btn_info['index']}].click();
                                    }}
                                """)
                                button_found = True
                                break
                    
                    # 方法4: 查找所有可点击元素
                    if not button_found:
                        print("查找所有可点击元素...")
                        clickable_elements = await page.evaluate("""
                            const elements = [];
                            // 查找所有button元素
                            document.querySelectorAll('button').forEach(el => {
                                elements.push({
                                    tag: 'button',
                                    text: el.textContent.trim(),
                                    rect: el.getBoundingClientRect()
                                });
                            });
                            // 查找所有a元素
                            document.querySelectorAll('a').forEach(el => {
                                elements.push({
                                    tag: 'a',
                                    text: el.textContent.trim(),
                                    rect: el.getBoundingClientRect()
                                });
                            });
                            // 查找所有有onclick属性的元素
                            document.querySelectorAll('[onclick]').forEach(el => {
                                elements.push({
                                    tag: el.tagName,
                                    text: el.textContent.trim(),
                                    rect: el.getBoundingClientRect()
                                });
                            });
                            return elements;
                        """)
                        
                        print(f"找到 {len(clickable_elements)} 个可点击元素")
                        for i, elem in enumerate(clickable_elements[:10]):  # 只显示前10个
                            if elem['text']:
                                print(f"  {i}: <{elem['tag']}> '{elem['text']}'")
                    
                    if button_found:
                        print("已点击验证码按钮！")
                        await page.wait_for_timeout(3000)
                        
                        # 检查是否发送成功
                        await page.screenshot(path="/root/vidu_captcha_check.png")
                        print("验证码发送检查截图已保存: /root/vidu_captcha_check.png")
                        
                        # 检查是否有错误提示
                        error_messages = await page.evaluate("""
                            const errors = [];
                            // 查找所有可能显示错误的元素
                            document.querySelectorAll('.error, .warning, [class*="error"], [class*="Error"]').forEach(el => {
                                if (el.textContent.trim()) {
                                    errors.push(el.textContent.trim());
                                }
                            });
                            // 查找所有toast提示
                            document.querySelectorAll('.toast, .notification, [class*="toast"], [class*="Toast"]').forEach(el => {
                                if (el.textContent.trim()) {
                                    errors.push(el.textContent.trim());
                                }
                            });
                            return errors;
                        """)
                        
                        if error_messages:
                            print("发现错误提示:")
                            for error in error_messages:
                                print(f"  - {error}")
                        else:
                            print("没有发现错误提示，验证码可能已发送")
                        
                        return True
                    else:
                        print("未找到验证码按钮")
                        return False
                else:
                    print("未找到手机号输入框")
                    return False
            except Exception as e:
                print(f"发送验证码失败: {e}")
                return False
            
            await browser.close()
    
    def handle_request(self, request):
        url = request.url
        method = request.method
        
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
    sender = ViduCaptchaSender(phone="13711967510")
    success = await sender.send_captcha()
    
    if success:
        print("=" * 60)
        print("验证码发送操作已完成！")
        print("请查看你的手机短信")
        print("如果收到验证码，请告诉我")
        print("如果没收到，可能需要检查手机号或重试")
        print("=" * 60)
    else:
        print("发送验证码失败")

if __name__ == "__main__":
    asyncio.run(main())
