# AI 赋能企业数字化转型 — 公网问卷

静态问卷（GitHub / Gitee Pages）+ **LeanCloud 国内版**集中收数 + 本地脚本生成报告。

**不依赖 Google**，大陆受访者与管理员均可正常使用。

## 架构

```
受访者 → 问卷网页（GitHub Pages 等）
              ↓ POST
         LeanCloud 国内节点（SurveyResponse 表）
              ↓ 本机脚本（Master Key，仅存 .env）
         output/survey_results.json → 汇总报告.md
```

## 快速开始

### 1. 配置 LeanCloud（约 10 分钟）

按 **[leancloud/部署说明.md](leancloud/部署说明.md)** 注册国内版、创建 Class、设置权限，并填写根目录 **`config.js`**。

### 2. 发布网页

```bash
git add config.js 调查问卷.html
git commit -m "配置 LeanCloud"
git push
```

GitHub：**Settings → Pages → main / (root)**  
访问：`https://你的用户名.github.io/仓库名/`

若 GitHub 较慢，可将同一目录同步到 **Gitee Pages** 或学校静态空间，**`config.js` 不变**即可共用同一数据库。

### 3. 生成二维码

```bash
python3 make_qrcode.py "https://你的问卷地址/"
```

### 4. 导出答卷做报告

```bash
cp .env.example .env   # 填入 Master Key，勿提交 Git
pip3 install requests
python3 scripts/fetch_submissions.py
python3 scripts/export_report.py output/survey_results.json -o output/汇总报告.md
```

也可在 LeanCloud 控制台直接 **导出 CSV**，用 Excel 做透视图。

## 文件说明

| 路径 | 说明 |
|------|------|
| `调查问卷.html` | 主问卷 |
| `config.js` | LeanCloud App ID / App Key（可公开） |
| `.env` | Master Key（仅本机，已 gitignore） |
| `leancloud/部署说明.md` | 国内收数配置步骤 |
| `scripts/fetch_submissions.py` | 拉取全部答卷 |
| `scripts/export_report.py` | 生成 Markdown 汇总 |
| `google-apps-script/` | 已弃用（需访问 Google） |

## 安全说明

- 网页中只放 **App Key**，且 Class 权限设为仅允许 `add`、禁止公开 `find`
- **Master Key** 只写在 `.env`，用于你自己电脑导出数据
