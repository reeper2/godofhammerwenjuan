#!/usr/bin/env python3
"""
阿里云问卷后端一键配置（杭州）。
需 RAM 用户的 AccessKey（在已登录控制台创建后粘贴到终端）。

用法：
  python3 aliyun/setup.py
  python3 aliyun/setup.py --access-key-id LTAI... --access-key-secret xxx
"""
from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGION = "cn-hangzhou"
OSS_ENDPOINT = "oss-cn-hangzhou.aliyuncs.com"
BUCKET_PREFIX = "gsl-survey-"
FC_ZIP = ROOT / "aliyun" / "fc-submit" / "fc-submit.zip"


def _open_urls() -> None:
    urls = [
        "https://ram.console.aliyun.com/users",
        "https://oss.console.aliyun.com/bucket",
        f"https://fcnext.console.aliyun.com/{REGION}/functions",
    ]
    for u in urls:
        try:
            subprocess.run(["open", u], check=False)
        except Exception:
            print("  ", u)


def _prompt_secret(label: str) -> str:
    try:
        import getpass

        return getpass.getpass(f"{label}: ").strip()
    except Exception:
        return input(f"{label}: ").strip()


def _write_env(bucket: str, ak: str, sk: str) -> None:
    env_path = ROOT / ".env"
    text = f"""# 由 aliyun/setup.py 生成 · 杭州
ALIYUN_OSS_ENDPOINT={OSS_ENDPOINT}
ALIYUN_OSS_BUCKET={bucket}
ALIYUN_ACCESS_KEY_ID={ak}
ALIYUN_ACCESS_KEY_SECRET={sk}
ALIYUN_OSS_PREFIX=survey-responses/
"""
    env_path.write_text(text, encoding="utf-8")
    print(f"已写入 {env_path}")


def _write_config(console_bucket: str, submit_url: str = "") -> None:
    cfg_path = ROOT / "config.js"
    submit = submit_url or "https://你的函数名.cn-hangzhou.fcapp.run"
    console = (
        f"https://oss.console.aliyun.com/bucket/oss-cn-hangzhou/"
        f"{console_bucket}/object?path=survey-responses%2F"
    )
    text = f"""// 由 aliyun/setup.py 生成 · 华东1（杭州）
window.SURVEY_CONFIG = {{
  aliyun: {{
    submitUrl: '{submit}',
    surveyToken: ''
  }},
  consoleUrl: '{console}'
}};
"""
    cfg_path.write_text(text, encoding="utf-8")
    print(f"已写入 {cfg_path}")


def ensure_bucket_v2(ak: str, sk: str) -> str:
    """使用 PutBucket API 创建杭州 bucket。"""
    import oss2

    auth = oss2.Auth(ak, sk)
    name = BUCKET_PREFIX + secrets.token_hex(4)
    bucket = oss2.Bucket(auth, f"https://{OSS_ENDPOINT}", name)
    try:
        bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)
    except oss2.exceptions.OssError as e:
        if getattr(e, "code", "") == "BucketAlreadyExists":
            name = BUCKET_PREFIX + secrets.token_hex(4)
            bucket = oss2.Bucket(auth, f"https://{OSS_ENDPOINT}", name)
            bucket.create_bucket(oss2.models.BUCKET_ACL_PRIVATE)
        elif getattr(e, "code", "") == "AccessDenied" and "PutBucket" in str(e):
            raise SystemExit(
                "当前 AccessKey 无权创建 Bucket。\n"
                "请在 OSS 控制台（杭州）手动创建私有 Bucket，然后执行：\n"
                "  python3 aliyun/setup.py --bucket 你的bucket名 --access-key-id ... --access-key-secret ..."
            ) from e
        else:
            raise
    bucket.put_object("survey-responses/.keep", b"")
    print(f"OSS Bucket 已就绪: {name}")
    return name


def print_fc_steps(bucket: str, ak: str, sk: str) -> None:
    print("\n" + "=" * 60)
    print("【请在浏览器完成函数计算 — 约 5 分钟】")
    print("已尝试打开：函数计算控制台（杭州）")
    print(f"ZIP 路径：{FC_ZIP}")
    print("\n1. 创建函数 → 上传 fc-submit.zip → 处理程序 index.handler")
    print("2. 环境变量：")
    print(f"   OSS_ENDPOINT={OSS_ENDPOINT}")
    print(f"   OSS_BUCKET={bucket}")
    print(f"   OSS_ACCESS_KEY_ID={ak[:6]}...")
    print("   OSS_ACCESS_KEY_SECRET=(你的 Secret)")
    print("   OSS_PREFIX=survey-responses/")
    print("3. 触发器 → HTTP → POST + OPTIONS → 匿名")
    print("4. 复制公网 URL 后执行：")
    print("   python3 aliyun/setup.py --submit-url 'https://xxx.cn-hangzhou.fcapp.run'")
    print("=" * 60)
    try:
        subprocess.run(
            ["open", f"https://fcnext.console.aliyun.com/{REGION}/functions"],
            check=False,
        )
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--access-key-id")
    parser.add_argument("--access-key-secret")
    parser.add_argument("--submit-url", help="函数 HTTP 地址，写入 config.js")
    parser.add_argument("--bucket", help="已存在的 OSS Bucket 名称（杭州）")
    parser.add_argument("--open-browser", action="store_true", help="打开阿里云控制台页面")
    args = parser.parse_args()

    if args.submit_url:
        env = ROOT / ".env"
        bucket = ""
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if line.startswith("ALIYUN_OSS_BUCKET="):
                    bucket = line.split("=", 1)[1].strip()
        if not bucket:
            bucket = "你的bucket"
        _write_config(bucket, args.submit_url.strip())
        print("config.js 已更新 submitUrl。请 git push 发布问卷页。")
        return

    ak = args.access_key_id or input("RAM AccessKey ID: ").strip()
    sk = args.access_key_secret or _prompt_secret("RAM AccessKey Secret")
    if not ak or not sk:
        print("需要 AccessKey。Firefox 登录不能代替 API 密钥。", file=sys.stderr)
        print("\n在已登录浏览器：RAM 控制台 → 用户 → 创建用户 → OpenAPI → 创建 AccessKey")
        if args.open_browser or input("是否打开 RAM 控制台？(y/n) ").strip().lower() == "y":
            _open_urls()
        sys.exit(1)

    try:
        import oss2  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "oss2", "-q"])

    if args.open_browser:
        _open_urls()

    if args.bucket:
        import oss2

        auth = oss2.Auth(ak, sk)
        bucket = args.bucket.strip()
        b = oss2.Bucket(auth, f"https://{OSS_ENDPOINT}", bucket)
        b.put_object("survey-responses/.keep", b"")
        print(f"已验证写入 Bucket: {bucket}")
    else:
        bucket = ensure_bucket_v2(ak, sk)
    _write_env(bucket, ak, sk)
    _write_config(bucket)
    print_fc_steps(bucket, ak, sk)


if __name__ == "__main__":
    main()
