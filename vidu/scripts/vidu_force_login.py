#!/usr/bin/env python3
"""
Vidu.cn 强制打开登录弹窗并发送验证码
"""

import asyncio
import json
from playwright.async_api import async_playwright

async def force_login():
    print("="*60)
    print("Vidu.cn 强制登录 - 手机号: 13711967510")
    print("="*60)
    
    phone = "13711967510"
    api_requests = []
    
    def capture_request(request):
        url = request.url
        if 'vidu' in url and not any(ext in url for ext in ['.js', '.css', '.png', '.jpg']):
            api_requests.append({
                "url": url,
                "method": request.method,
                "post_data": request.post_data
            })
            print(f"  API: {request.method} {url[:60]}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox']
        )
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        page.on("request", capture_request)
        
        # 访问页面
        print("\n[1] 访问 Vidu.cn/create/text2video...")
        await page.goto("https://www.vidu.cn/create/text2video", wait_until="networkidle")
        await page.wait_for_timeout(5000)
        
        # 强制点击登录 - 使用多种方法
        print("\n[2] 强制点击登录按钮...")
        
        # 方法1: 找所有包含"登录"文字的元素并点击
        clicked = await page.evaluate("""() => {
            const results = [];
            // 找所有元素
            const allElements = document.querySelectorAll('*');
            for (const el of allElements) {
                if (el.textContent && el.textContent.trim() === '登录' && 
                    el.offsetParent !== null && 
                    (el.tagName === 'BUTTON' || el.tagName === 'A' || el.tagName === 'SPAN' || el.tagName === 'DIV')) {
                    results.push({
                        tag: el.tagName,
                        text: el.textContent.trim(),
                        class: el.className
                    });
                    el.click();
                }
            }
            return results;
        }""")
        
        print(f"    找到并点击了 {len(clicked)} 个登录元素:")
        for item in clicked:
            print(f"      - <{item['tag']}> class='{item['class'][:50]}'")
        
        await page.wait_for_timeout(5000)
        
        # 截图看看
        await page.screenshot(path="/root/vidu_force_login1.png")
        print("    截图: /root/vidu_force_login1.png")
        
        # 检查是否有弹窗出现
        print("\n[3] 检查登录弹窗...")
        dialog_info = await page.evaluate("""() => {
            // 检查所有可能的弹窗容器
            const selectors = [
                '[role="dialog"]',
                '[class*="modal"]',
                '[class*="Modal"]',
                '[class*="dialog"]',
                '[class*="Dialog"]',
                '[class*="popup"]',
                '[class*="Popup"]',
                '[class*="login"]',
                '[class*="Login"]',
                '[class*="auth"]'
            ];
            
            const results = [];
            for (const sel of selectors) {
                const elements = document.querySelectorAll(sel);
                for (const el of elements) {
                    if (el.offsetParent !== null || el.style.display !== 'none') {
                        results.push({
                            selector: sel,
                            tag: el.tagName,
                            class: el.className.toString().substring(0, 100),
                            children: el.children.length,
                            hasInput: el.querySelectorAll('input').length,
                            hasButton: el.querySelectorAll('button').length
                        });
                    }
                }
            }
            return results;
        }""")
        
        print(f"    找到 {len(dialog_info)} 个可能的弹窗:")
        for info in dialog_info:
            print(f"      {info['selector']}: inputs={info['hasInput']}, buttons={info['hasButton']}")
        
        # 如果有弹窗有输入框，尝试输入
        if any(info['hasInput'] > 0 for info in dialog_info):
            print("\n[4] 找到有输入框的弹窗，尝试输入手机号...")
            
            # 尝试填充所有可见输入框
            inputs = await page.evaluate("""() => {
                const inputs = document.querySelectorAll('input');
                return Array.from(inputs).filter(inp => inp.offsetParent !== null).map((inp, i) => ({
                    index: i,
                    type: inp.type,
                    placeholder: inp.placeholder,
                    name: inp.name
                }));
            }""")
            
            print(f"    找到 {len(inputs)} 个可见输入框:")
            for inp in inputs:
                print(f"      [{inp['index']}] type={inp['type']} placeholder='{inp['placeholder']}'")
            
            # 尝试在第一个输入框输入手机号
            if inputs:
                try:
                    # 使用JavaScript直接设置值
                    await page.evaluate(f"""(phone) => {{
                        const inputs = document.querySelectorAll('input');
                        const visibleInputs = Array.from(inputs).filter(inp => inp.offsetParent !== null);
                        if (visibleInputs.length > 0) {{
                            visibleInputs[0].value = phone;
                            visibleInputs[0].dispatchEvent(new Event('input', {{ bubbles: true }}));
                            visibleInputs[0].dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }}""", phone)
                    print(f"    输入手机号: {phone}")
                except Exception as e:
                    print(f"    输入失败: {e}")
            
            await page.wait_for_timeout(1000)
            await page.screenshot(path="/root/vidu_force_login2.png")
            print("    截图: /root/vidu_force_login2.png")
            
            # 尝试点击发送验证码
            print("\n[5] 尝试点击发送验证码...")
            captcha_clicked = await page.evaluate("""() => {
                const buttons = document.querySelectorAll('button');
                for (const btn of buttons) {
                    const text = btn.textContent || '';
                    if ((text.includes('获取') || text.includes('发送') || text.includes('验证码')) && 
                        btn.offsetParent !== null && !btn.disabled) {
                        btn.click();
                        return {clicked: true, text: text};
                    }
                }
                return {clicked: false};
            }""")
            
            if captcha_clicked['clicked']:
                print(f"    点击了按钮: '{captcha_clicked['text']}'")
                await page.wait_for_timeout(3000)
            else:
                print("    未找到验证码按钮")
            
            await page.screenshot(path="/root/vidu_force_login3.png")
            print("    截图: /root/vidu_force_login3.png")
        else:
            print("\n[4] 未找到登录弹窗，尝试其他方式...")
            
            # 尝试直接访问登录页面
            print("    尝试直接访问登录页面...")
            await page.goto("https://www.vidu.cn/login", wait_until="networkidle")
            await page.wait_for_timeout(3000)
            
            await page.screenshot(path="/root/vidu_force_login_direct.png")
            print("    截图: /root/vidu_force_login_direct.png")
            
            # 检查输入框
            inputs = await page.evaluate("""() => {
                const inputs = document.querySelectorAll('input');
                return Array.from(inputs).map((inp, i) => ({
                    index: i,
                    type: inp.type,
                    placeholder: inp.placeholder,
                    visible: inp.offsetParent !== null
                }));
            }""")
            
            print(f"    找到 {len(inputs)} 个输入框:")
            for inp in inputs:
                print(f"      [{inp['index']}] type={inp['type']} placeholder='{inp['placeholder']}' visible={inp['visible']}")
        
        # 保存API请求
        print(f"\n[6] 捕获到 {len(api_requests)} 个API请求")
        with open("/root/vidu_force_login_apis.json", "w") as f:
            json.dump(api_requests, f, indent=2, ensure_ascii=False)
        
        await browser.close()
    
    print("\n" + "="*60)
    print("完成！请检查截图:")
    print("  - /root/vidu_force_login1.png")
    print("  - /root/vidu_force_login2.png")
    print("  - /root/vidu_force_login3.png")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(force_login())
