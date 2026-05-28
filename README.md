# AI 赋能企业数字化转型 — 公网问卷

静态问卷页面（GitHub Pages）+ Google 表格集中收集答卷 + 本地脚本生成汇总报告。

## 架构

```
受访者浏览器 → GitHub Pages（调查问卷.html）
                    ↓ POST
              Google Apps Script Web 应用
                    ↓
              Google 表格 responses 表
                    ↓ 导出 CSV
              scripts/export_report.py → 汇总报告.md
```

## 快速开始（三步）

### 第一步：部署数据收集（必做）

按 [google-apps-script/部署说明.md](google-apps-script/部署说明.md) 配置 Google 表格与 Apps Script，并填写根目录 `config.js`。

> 未完成此步时，访客提交会提示「数据服务尚未配置」。

### 第二步：发布到 GitHub Pages

```bash
cd "/Users/moon/Pool/01_Projects/2605_gsl问卷公网发送"

# 若尚未初始化
git init
git add .
git commit -m "问卷站点：GitHub Pages + Google 表格收集"

# 在 github.com 新建仓库（如 gsl-survey），不要勾选 README
git branch -M main
git remote add origin https://github.com/你的用户名/gsl-survey.git
git push -u origin main
```

在 GitHub 仓库：**Settings → Pages → Source** 选 **main** 分支、**/(root)**，保存。

约 1–2 分钟后访问：

`https://你的用户名.github.io/gsl-survey/`

（`index.html` 会自动跳转到 `调查问卷.html`）

### 第三步：生成分享二维码

```bash
python3 make_qrcode.py "https://你的用户名.github.io/gsl-survey/"
```

得到 `问卷二维码.png`，可插入海报或微信。

## 管理员查看数据

| 方式 | 说明 |
|------|------|
| Google 表格 | 打开 `config.js` 中的 `sheetUrl`，实时查看所有行 |
| 问卷页管理员 | 输入 `adminKey`，在页面查看详情并导出 JSON |
| 汇总报告 | `python3 scripts/export_report.py 导出的.csv -o output/汇总报告.md` |

## 仓库文件说明

| 文件 | 作用 |
|------|------|
| `调查问卷.html` | 主问卷页面 |
| `index.html` | Pages 入口跳转 |
| `config.js` | 提交地址、管理员密钥、表格链接 |
| `google-apps-script/Code.gs` | 服务端写入表格逻辑 |
| `scripts/export_report.py` | 从 CSV/JSON 生成 Markdown 汇总 |
| `make_qrcode.py` | 生成分享二维码 |

## 更新问卷后

```bash
git add .
git commit -m "更新问卷内容"
git push
```

Pages 会自动重新部署。

## 常见问题

**Q：为什么不用 localStorage？**  
每人浏览器各自存储，无法汇总。公网发放必须使用 Google 表格（或同类云端后端）。

**Q：config.js 里的 adminKey 安全吗？**  
仅用于方便在网页查看列表；真正权限由 Apps Script 脚本属性 `ADMIN_KEY` 控制。勿使用过于简单的密码。

**Q：能否不用 Google？**  
可以，但需另接 Supabase、腾讯云开发等数据库，并修改 `调查问卷.html` 中的提交逻辑。当前方案零服务器费用、最适合做 Excel 报告。
