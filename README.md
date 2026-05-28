# AI 赋能企业数字化转型 — 公网问卷

静态问卷页面 + **阿里云函数计算 + OSS** 收数 + 本机脚本生成报告。

国内可访问，不依赖 Google / LeanCloud。

## 架构

```
受访者 → 问卷网页（GitHub / Gitee Pages）
              ↓ POST
         阿里云函数计算（HTTP 触发器）
              ↓
         OSS：survey-responses/*.json

管理员 → python3 scripts/fetch_submissions.py → 汇总报告
```

## 快速开始

### 1. 部署阿里云后端（约 20–30 分钟）

按 **[aliyun/部署说明.md](aliyun/部署说明.md)** 完成：

- OSS 私有存储桶  
- RAM AccessKey（勿泄露 Master 账号密钥）  
- 函数计算上传 `aliyun/fc-submit` 打包代码  
- HTTP 触发器公网地址  

### 2. 配置问卷

编辑 **`config.js`**：

```javascript
window.SURVEY_CONFIG = {
  aliyun: {
    submitUrl: 'https://你的函数.fcapp.run',
    surveyToken: ''  // 可选，与函数环境变量 SURVEY_TOKEN 一致
  },
  consoleUrl: 'https://oss.console.aliyun.com/...'
};
```

`git push` 更新 GitHub Pages。

### 3. 分享

```bash
python3 make_qrcode.py "https://你的用户名.github.io/仓库名/"
```

### 4. 导出答卷

```bash
cp .env.example .env   # 填写 OSS 与 AccessKey
pip3 install oss2
python3 scripts/fetch_submissions.py
python3 scripts/export_report.py output/survey_results.json -o output/汇总报告.md
```

## 安全说明

| 位置 | 内容 |
|------|------|
| 网页 `config.js` | 仅函数 **公网 URL**（及可选 surveyToken） |
| 函数环境变量 | OSS AccessKey（访客无法看到） |
| 本机 `.env` | 同上，用于导出（已 gitignore） |

## 目录

| 路径 | 说明 |
|------|------|
| `调查问卷.html` | 主问卷 |
| `aliyun/fc-submit/` | 函数计算源码 |
| `aliyun/部署说明.md` | 阿里云配置步骤 |
| `scripts/fetch_submissions.py` | 从 OSS 拉取全部答卷 |
| `leancloud/`、`google-apps-script/` | 已弃用方案 |
