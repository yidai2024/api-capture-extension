# Vidu.cn API 接口文档

> 抓取时间: 2026-04-14  
> 工具: Playwright (Headless Chrome)  
> 总端点数: 90+

---

## 目录

- [1. 核心业务 API (service.vidu.cn)](#1-核心业务-api)
- [2. 前端页面 API (www.vidu.cn)](#2-前端页面-api)
- [3. 第三方服务 API](#3-第三方服务-api)
- [4. CDN 资源](#4-cdn-资源)
- [5. 请求头规范](#5-请求头规范)
- [6. 登录流程](#6-登录流程)
- [7. 支持的视频生成类型](#7-支持的视频生成类型)
- [8. 技术架构](#8-技术架构)

---

## 1. 核心业务 API

基础域名: `https://service.vidu.cn`

### 1.1 用户认证与管理

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/iam/v1/users/me` | 获取当前登录用户信息 | 是 |
| POST | `/iam/v1/users/send-auth-code` | 发送手机验证码 | 否 |
| POST | `/iam/v1/tracks/update` | 用户行为追踪上报 | 否 |

#### GET /iam/v1/users/me

获取当前登录用户的详细信息。

```
GET https://service.vidu.cn/iam/v1/users/me

Headers:
  x-platform: web
  x-app-version: -
  accept-language: zh
  referer: https://www.vidu.cn/

Response: 用户信息 JSON
```

#### POST /iam/v1/users/send-auth-code

发送手机验证码用于登录。

```
POST https://service.vidu.cn/iam/v1/users/send-auth-code

Headers:
  x-platform: web
  Content-Type: application/json

Body:
{
  "phone": "13xxxxxxxxx",
  "area_code": "+86"
}
```

#### POST /iam/v1/tracks/update

上报用户行为数据。

```
POST https://service.vidu.cn/iam/v1/tracks/update

Headers:
  x-platform: web
  x-request-id: <uuid>
  Content-Type: application/json

Body:
{
  "device_id": "DEVICE_<uuid>",
  "meta_data": {
    "utm_source": "",
    "utm_campaign": "",
    "utm_term": "",
    "utm_content": "",
    "utm_medium": "",
    "logidUrl": ""
  }
}
```

---

### 1.2 视频任务管理

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/vidu/v1/region` | 获取用户地区信息 | 否 |
| GET | `/vidu/v1/page-config?keys=template_entrance_tag` | 获取页面配置 | 否 |
| GET | `/vidu/v1/tasks/count` | 获取各状态任务数量统计 | 是 |
| GET | `/vidu/v1/tasks/credits` | 获取任务所需积分 | 是 |

#### GET /vidu/v1/region

```
GET https://service.vidu.cn/vidu/v1/region

Response:
{
  "region": "CN",
  "country": "china"
}
```

#### GET /vidu/v1/tasks/count

获取各状态、各类型任务的数量。

```
GET https://service.vidu.cn/vidu/v1/tasks/count
    ?states=created&states=queueing&states=preparation
    &states=scheduling&states=processing
    &types=img2video&types=character2video&types=text2video
    &types=reference2image&types=text2image&types=image_edit
    &types=video_edit&types=upscale&types=extend
    &types=face_swap&types=lip_sync&types=music_video
    ...

Parameters:
  states: 任务状态数组 (created, queueing, preparation, scheduling, processing)
  types: 任务类型数组
```

#### GET /vidu/v1/tasks/credits

获取生成视频所需积分。

```
GET https://service.vidu.cn/vidu/v1/tasks/credits
    ?type=text2video
    &settings.duration=8
    &settings.resolution=1080p
    &settings.movement_amplitude=auto
    &settings.aspect_ratio=16:9
    &settings.sample_count=1
    &settings.schedule_mode=normal
    &settings.transition=pro
    &settings.codec=h264
    &settings.model_version=3.2
    &settings.use_trial=false

Parameters:
  type: 任务类型 (text2video, img2video, etc.)
  settings.duration: 视频时长 (秒)
  settings.resolution: 分辨率 (720p, 1080p)
  settings.aspect_ratio: 宽高比 (16:9, 9:16, 1:1)
  settings.model_version: 模型版本
  settings.use_trial: 是否使用试用
```

---

### 1.3 支付与订单

| 方法 | 端点 | 说明 | 需要登录 |
|------|------|------|----------|
| GET | `/credit/v1/orders/products/filter?channels=alipay` | 获取可购买产品列表 | 是 |

```
GET https://service.vidu.cn/credit/v1/orders/products/filter?channels=alipay

Parameters:
  channels: 支付渠道 (alipay, wechat)
```

---

## 2. 前端页面 API

基础域名: `https://www.vidu.cn`

Vidu 使用 Next.js 的 React Server Components (RSC)，页面切换时会请求带 `_rsc` 参数的端点。

### 2.1 页面端点

| 页面路径 | 说明 |
|----------|------|
| `/` | 首页 |
| `/home` | 主页 |
| `/home/recommend` | 推荐内容 |
| `/home/tutorial` | 教程 |
| `/create/text2video` | 文本生成视频 |
| `/create/img2video` | 图片生成视频 |
| `/create/character2video` | 角色生成视频 |
| `/templates` | 模板页面 |
| `/pricing` | 价格页面 |
| `/vidu-claw` | Vidu Claw 功能 |
| `/help-center` | 帮助中心 |
| `/terms` | 服务条款 |
| `/privacy` | 隐私政策 |

### 2.2 其他前端 API

| 端点 | 说明 |
|------|------|
| `/api/canary?deviceId=<id>&userId=<id>` | 功能开关/灰度发布检测 |

---

## 3. 第三方服务 API

| 服务商 | URL | 用途 |
|--------|-----|------|
| 百度统计 | `https://fclog.baidu.com/log/ocpcagl?type=behavior&emd=euc` | 用户行为分析 |
| 百度统计 | `https://hm.baidu.com/hm.gif?...` | 页面访问统计 |
| 字节跳动 | `https://gator.volces.com/webid` | 用户标识 |
| 字节跳动 | `https://gator.volces.com/list` | 数据上报 |
| Microsoft Clarity | `https://i.clarity.ms/collect` | 用户行为录制 |
| Sentry | `https://trace.shengshu-ai.com/api/10/envelope/...` | 错误监控 |
| Bing | `https://bat.bing.com/action/0?...` | 转化追踪 |

---

## 4. CDN 资源

基础域名: `https://image01.vidu.zone`

| 资源路径 | 说明 |
|----------|------|
| `/vidu/media-asset/q3-r2v-bg-*.webp` | 视频背景图 |
| `/vidu/media-asset/q3-r2v-illustration-*.webp` | 插图素材 |
| `/vidu/media-asset/q3_r2v_title_zh-*.webp` | 标题图片 |
| `/vidu/media-asset/q3-*.webp` | 功能展示图 |
| `/vidu/media-asset/q2-*.webp` | 季度活动图 |
| `/vidu/media-asset/Q1-*.webp` | 一季度活动图 |
| `/vidu/media-asset/credit_left-*.webp` | 积分图标左 |
| `/vidu/media-asset/credit_right-*.webp` | 积分图标右 |
| `/vidu/media-asset/invite-friends-dialog-header-zh-*.webp` | 邀请好友弹窗头部 |

---

## 5. 请求头规范

核心业务 API 的通用请求头:

```
x-platform: web
x-app-version: -
accept-language: zh
referer: https://www.vidu.cn/
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
sec-ch-ua: "Not:A-Brand";v="99", "Chromium";v="120"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
```

POST 请求额外需要:
```
Content-Type: application/json
x-request-id: <uuid-v4>
```

---

## 6. 登录流程

```
┌─────────────────────────────────────────┐
│  1. 访问 vidu.cn                        │
│  2. 点击"登录/注册"按钮                  │
│  3. 输入手机号                           │
│  4. 点击"登录/注册" → 自动发送 SMS       │
│     POST /iam/v1/users/send-auth-code   │
│  5. 输入验证码                           │
│  6. 完成登录，获取 session cookie        │
└─────────────────────────────────────────┘
```

**注意**: vidu.cn 没有单独的"获取验证码"按钮，点击"登录/注册"会自动发送 SMS 验证码。

---

## 7. 支持的视频生成类型

| 类型 | 说明 |
|------|------|
| `text2video` | 文本生成视频 |
| `img2video` | 图片生成视频 |
| `character2video` | 角色生成视频 |
| `reference2image` | 参考图生成 |
| `text2image` | 文本生成图片 |
| `image_edit` | 图片编辑 |
| `video_edit` | 视频编辑 |
| `upscale` | 视频超分 |
| `extend` | 视频延长 |
| `face_swap` | 换脸 |
| `lip_sync` | 对口型 |
| `music_video` | 音乐视频 |
| `headtailimg2video` | 首尾帧视频 |
| `multi_frame` | 多帧控制 |
| `controlnet` | ControlNet 控制 |
| `material2video` | 素材生成视频 |
| `video2extend` | 视频延长扩展 |
| `video2extail` | 视频尾部扩展 |
| `upscale_image` | 图片超分 |
| `one_click` | 一键生成 |
| `remake` | 重新制作 |

---

## 8. 技术架构

```
┌──────────────────────────────────────────────────┐
│                    Vidu.cn 前端                   │
│           Next.js + React Server Components       │
├──────────────────────────────────────────────────┤
│  www.vidu.cn          │  image01.vidu.zone       │
│  (页面 + RSC)         │  (CDN 静态资源)          │
├───────────────────────┴──────────────────────────┤
│              service.vidu.cn                     │
│              (RESTful API 后端)                  │
├──────────────────────────────────────────────────┤
│  认证: Cookie/Session                           │
│  反爬虫: 腾讯 EdgeOne                           │
│  监控: Sentry                                   │
│  分析: 百度统计 + 字节跳动 + Microsoft Clarity   │
└──────────────────────────────────────────────────┘
```

---

## 附录: 完整 API 列表 (按域名分组)

### service.vidu.cn (核心 API)
```
GET  /iam/v1/users/me
POST /iam/v1/users/send-auth-code
POST /iam/v1/tracks/update
GET  /vidu/v1/region
GET  /vidu/v1/page-config?keys=template_entrance_tag
GET  /vidu/v1/tasks/count?states=...&types=...
GET  /vidu/v1/tasks/credits?type=...&settings=...
GET  /credit/v1/orders/products/filter?channels=alipay
```

### www.vidu.cn (前端 API)
```
GET  /api/canary?deviceId=...&userId=...
GET  /?_rsc=...
GET  /home?_rsc=...
GET  /home/recommend?_rsc=...
GET  /home/tutorial?_rsc=...
GET  /create/text2video?_rsc=...
GET  /create/img2video?_rsc=...
GET  /create/character2video?_rsc=...
GET  /templates?_rsc=...
GET  /pricing?_rsc=...
GET  /vidu-claw?_rsc=...
GET  /help-center?_rsc=...
GET  /terms?_rsc=...
GET  /privacy?_rsc=...
```

---

*文档由 Playwright 自动抓取生成*
