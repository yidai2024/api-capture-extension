# Vidu.cn API Capture

使用 Playwright 自动化抓取 vidu.cn 的 API 接口。

## 目录结构

```
vidu/
├── reports/          # 分析报告
│   ├── vidu_api_guide.md          # API 使用指南
│   ├── vidu_api_complete_report.txt  # 完整报告
│   └── vidu_final_report.txt      # 最终报告
├── data/             # JSON 数据
│   ├── vidu_results.json          # 原始抓取结果
│   ├── vidu_organized_apis.json   # 整理后的 API
│   ├── vidu_force_login_apis.json # 登录相关 API
│   ├── vidu_login_state.json      # 登录状态详情
│   └── ...
└── scripts/          # Python 脚本
    ├── vidu_scraper.py            # 基础抓取脚本
    ├── vidu_login.py              # 登录自动化
    ├── vidu_final_login.py        # 最终登录方案
    └── ...
```

## 核心 API（service.vidu.cn）

| 端点 | 方法 | 用途 |
|------|------|------|
| `/iam/v1/users/me` | GET | 获取用户信息 |
| `/iam/v1/users/send-auth-code` | POST | 发送验证码 |
| `/vidu/v1/region` | GET | 获取地区 |
| `/vidu/v1/tasks/count` | GET | 任务数量 |
| `/vidu/v1/tasks/credits` | GET | 积分消耗 |
| `/credit/v1/orders/products/filter` | GET | 产品价格 |

## 技术发现

1. **反爬虫**: vidu 使用腾讯 EdgeOne 保护
2. **登录流程**: 输入手机号 → 点击"登录/注册" → 自动发送 SMS → 输入验证码
3. **前端技术**: Next.js + React Server Components
4. **CDN**: image01.vidu.zone

## 问题

登录弹窗的遮罩层会阻挡点击事件，需要 JS 绕过。
