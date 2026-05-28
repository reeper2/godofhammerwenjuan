# AGENTS.md — 问卷公网发送

## 项目本质

静态问卷（`调查问卷.html` / `index.html`）→ POST → 阿里云函数计算（杭州）→ OSS 存 JSON。前端无构建，纯静态托管于 GitHub/Gitee Pages。

## 关键约束

- **所有阿里云资源必须在 华东1（杭州）**。OSS 与函数计算必须同地域，否则 FC 无法写 OSS。
- **两个配置文件**：`config.js`（提交 URL，可提交 Git）和 `.env`（含 AccessKey，已 gitignore，**禁止提交**）。
- `aliyun/AccessKey.md` 包含明文的 AccessKey——绝对不要 `git add` 此文件。

## 开发者命令

### 部署阿里云后端

```bash
# 一键配置（创建 Bucket、写入 .env 和 config.js）
python3 aliyun/setup.py

# 如 AccessKey 无权创建 Bucket，控制台手动建好后补跑：
python3 aliyun/setup.py --bucket gsl-survey-hz-moon \
  --access-key-id '...' --access-key-secret '...'

# FC 部署完成后写入 submitUrl（第二次运行 setup.py）
python3 aliyun/setup.py --submit-url 'https://xxx.cn-hangzhou.fcapp.run'
```

### 打包函数计算

`aliyun/fc-submit/index.py` 变更后需重新打包：

```bash
cd aliyun/fc-submit
pip3 install -r requirements.txt -t ./package
cp index.py ./package/
cd package && zip -r ../fc-submit.zip . && cd ../..
```

FC 配置：Python 3.10、处理程序 `index.handler`、256MB、30s 超时、HTTP 触发器 POST+OPTIONS 匿名。

### 生成二维码

```bash
python3 make_qrcode.py "https://你的用户名.github.io/仓库名/"
```

### 导出答卷

```bash
pip3 install oss2 pandas
python3 scripts/fetch_submissions.py            # → output/survey_results.json
python3 scripts/export_report.py output/survey_results.json -o output/汇总报告.md
```

## 架构要点

- 所有脚本以项目根目录为 `ROOT`，通过 `Path(__file__).parents[]` 定位——从任意位置跑 `python3 scripts/xxx.py` 均可。
- `aliyun/setup.py` 是**有状态脚本**：首次运行创建 Bucket + 写 `.env` + 写 `config.js` 占位；`--submit-url` 模式只更新 `config.js` 的 URL。
- 问卷 POST 的 JSON 体包含 `payload` 字段（嵌套问卷数据）。FC 存盘 key 格式：`survey-responses/{timestamp}_{uuid}.json`。
- `SURVEY_TOKEN` 环境变量可选防刷：若设置，`config.js` 需传同名 token（`X-Survey-Token` 请求头）。
- 本机导出脚本从 `.env` 读取凭据，也支持环境变量覆盖。
- 当前 git 未配置 remote，`git push` 前需先 `git remote add`。

## 风格与惯例

- 无 linter/formatter/typechecker 配置——仅 Python + 纯前端 JS，无需额外工具。
- `.env` 放在根目录。Python 脚本用 `load_env()` 解析（兼容 env 文件与环境变量）。
- 提交前确认 `.env`、`__pycache__/`、`output/`、`aliyun/fc-submit/package/`、`*.zip` 未被跟踪（见 `.gitignore`）。
