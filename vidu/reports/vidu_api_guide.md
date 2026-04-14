# Vidu AI视频生成平台 API接口抓取指南

## 概述
Vidu网站（https://www.vidu.cn）使用了腾讯云EdgeOne反爬虫保护，需要使用浏览器开发者工具来抓取真实API接口。

## 抓取步骤

### 第一步：打开浏览器开发者工具
1. 打开Chrome浏览器，访问 https://www.vidu.cn
2. 按F12打开开发者工具
3. 切换到Network面板
4. 勾选"Preserve log"选项

### 第二步：登录并抓取接口
1. 在网站上登录你的账号
2. 在Network面板中观察所有请求
3. 特别关注XHR/Fetch类型的请求

### 第三步：抓取以下关键接口

#### 1. 用户登录接口
- **接口URL**: 通常是 `/api/auth/login` 或类似路径
- **请求方法**: POST
- **请求头**:
  ```
  Content-Type: application/json
  Cookie: [登录前的Cookie]
  ```
- **请求体**:
  ```json
  {
    "username": "你的用户名/邮箱",
    "password": "你的密码",
    "captcha": "验证码（如果有）"
  }
  ```
- **响应**: 通常返回token或设置Cookie

#### 2. 获取用户信息接口
- **接口URL**: 通常是 `/api/user/info` 或 `/api/user/profile`
- **请求方法**: GET
- **请求头**:
  ```
  Authorization: Bearer [token]
  Cookie: [登录后的Cookie]
  ```

#### 3. 查询免费额度接口
- **接口URL**: 通常是 `/api/user/credit` 或 `/api/user/quota`
- **请求方法**: GET
- **请求头**:
  ```
  Authorization: Bearer [token]
  Cookie: [登录后的Cookie]
  ```

#### 4. 文生视频提交任务接口
- **接口URL**: 通常是 `/api/video/text2video` 或 `/api/generate/text`
- **请求方法**: POST
- **请求头**:
  ```
  Content-Type: application/json
  Authorization: Bearer [token]
  Cookie: [登录后的Cookie]
  ```
- **请求体**:
  ```json
  {
    "prompt": "视频描述文本",        // 必须字段
    "negativePrompt": "负面提示词",  // 可选
    "style": "视频风格",            // 可选
    "aspectRatio": "16:9",          // 可选
    "duration": 4,                  // 可选，视频时长
    "seed": 123456                  // 可选，随机种子
  }
  ```

#### 5. 图生视频提交任务接口
- **接口URL**: 通常是 `/api/video/img2video` 或 `/api/generate/image`
- **请求方法**: POST
- **请求头**:
  ```
  Content-Type: multipart/form-data
  Authorization: Bearer [token]
  Cookie: [登录后的Cookie]
  ```
- **请求体** (form-data):
  ```
  image: [图片文件]               // 必须字段
  prompt: "补充描述文本"          // 可选
  motionStrength: 0.7             // 可选，运动强度
  ```

#### 6. 任务进度查询接口
- **接口URL**: 通常是 `/api/task/{taskId}` 或 `/api/generate/status/{taskId}`
- **请求方法**: GET
- **请求头**:
  ```
  Authorization: Bearer [token]
  Cookie: [登录后的Cookie]
  ```

#### 7. 获取视频下载地址接口
- **接口URL**: 通常是 `/api/video/download/{videoId}` 或 `/api/video/{videoId}/url`
- **请求方法**: GET
- **请求头**:
  ```
  Authorization: Bearer [token]
  Cookie: [登录后的Cookie]
  ```

## 关键字段说明

### 必须字段
- **登录接口**: `username`, `password`
- **文生视频**: `prompt`
- **图生视频**: `image` (文件)
- **所有业务接口**: `Authorization`头 或 `Cookie`

### 可选字段
- `prompt`: 视频描述文本
- `image`: 参考图片文件
- `duration`: 视频时长（秒）
- `aspectRatio`: 宽高比（如 "16:9", "9:16"）
- `style`: 视频风格
- `negativePrompt`: 负面提示词
- `seed`: 随机种子

## 批量调用格式

### Python示例代码框架
```python
import requests
import json

class ViduAPI:
    def __init__(self, token, cookie):
        self.base_url = "https://www.vidu.cn"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Authorization": f"Bearer {token}",
            "Cookie": cookie
        }
    
    def login(self, username, password):
        """登录接口"""
        url = f"{self.base_url}/api/auth/login"
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def get_user_info(self):
        """获取用户信息"""
        url = f"{self.base_url}/api/user/info"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_credits(self):
        """查询免费额度"""
        url = f"{self.base_url}/api/user/credit"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def text_to_video(self, prompt, duration=4, aspect_ratio="16:9"):
        """文生视频"""
        url = f"{self.base_url}/api/video/text2video"
        data = {
            "prompt": prompt,
            "duration": duration,
            "aspectRatio": aspect_ratio
        }
        response = requests.post(url, json=data, headers=self.headers)
        return response.json()
    
    def image_to_video(self, image_path, prompt=""):
        """图生视频"""
        url = f"{self.base_url}/api/video/img2video"
        files = {"image": open(image_path, "rb")}
        data = {"prompt": prompt}
        response = requests.post(url, files=files, data=data, headers=self.headers)
        return response.json()
    
    def get_task_status(self, task_id):
        """查询任务状态"""
        url = f"{self.base_url}/api/task/{task_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    def get_video_url(self, video_id):
        """获取视频下载地址"""
        url = f"{self.base_url}/api/video/download/{video_id}"
        response = requests.get(url, headers=self.headers)
        return response.json()

# 使用示例
if __name__ == "__main__":
    # 需要先获取token和cookie
    token = "你的token"
    cookie = "你的cookie"
    
    api = ViduAPI(token, cookie)
    
    # 登录
    # result = api.login("用户名", "密码")
    
    # 获取用户信息
    # user_info = api.get_user_info()
    
    # 文生视频
    # task = api.text_to_video("一只猫在跳舞")
    
    # 查询任务状态
    # status = api.get_task_status("任务ID")
```

## 注意事项

1. **Cookie和Token**: 登录后会获得Cookie和Token，所有业务接口都需要这两个认证信息
2. **接口版本**: 实际接口路径可能包含版本号，如 `/api/v1/...`
3. **请求频率**: 注意请求频率限制，避免被封号
4. **验证码**: 登录可能需要验证码，需要额外处理
5. **文件上传**: 图生视频接口需要上传文件，使用multipart/form-data格式

## 下一步行动

1. 使用浏览器访问 https://www.vidu.cn
2. 按F12打开开发者工具
3. 登录账号
4. 在Network面板中抓取实际API接口
5. 复制完整的请求信息（URL、请求头、请求体）
6. 填入上面的代码框架中

抓取完成后，你就可以批量调用Vidu的API接口了。