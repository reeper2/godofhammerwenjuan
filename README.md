# AI 赋能企业数字化转型 — 公网问卷

静态问卷 + **阿里云（杭州）函数计算 + OSS** 收数 + 本机脚本生成报告。

## 架构

```
受访者 → 问卷网页（GitHub Pages）
              ↓ POST
         函数计算（杭州 · HTTP 触发器）
              ↓
         OSS 杭州：survey-responses/*.json

管理员 → fetch_submissions.py → 汇总报告.md
```

## 快速开始

### 1. 部署阿里云（杭州）

按 **[aliyun/部署说明.md](aliyun/部署说明.md)** 配置 OSS、RAM、函数计算，地域统一选 **华东1（杭州）**。

### 2. 填写 config.js

```javascript
window.SURVEY_CONFIG = {
  aliyun: {
    submitUrl: 'https://xxx.cn-hangzhou.fcapp.run',
    surveyToken: ''
  },
  consoleUrl: 'https://oss.console.aliyun.com/bucket/oss-cn-hangzhou/你的bucket/...'
};
```

### 3. 发布网页并生成二维码

```bash
git push
python3 make_qrcode.py "https://你的用户名.github.io/仓库名/"
```

### 4. 导出答卷

```bash
cp .env.example .env   # 杭州 endpoint 已写好
pip3 install oss2
python3 scripts/fetch_submissions.py
python3 scripts/export_report.py output/survey_results.json -o output/汇总报告.md
```

## 目录

| 路径 | 说明 |
|------|------|
| `调查问卷.html` | 主问卷 |
| `aliyun/` | 函数计算源码与部署说明 |
| `config.js` | 提交接口地址（可提交到 Git） |
| `.env` | AccessKey，仅本机（已 gitignore） |
| `scripts/` | 导出与报告脚本 |
