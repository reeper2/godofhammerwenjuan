#!/usr/bin/env python3
"""配置 OSS 静态网站托管 + 上传问卷文件。"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.fetch_submissions import load_env  # reuse env parser


def main():
    env = load_env()
    bucket_name = env["ALIYUN_OSS_BUCKET"]
    endpoint = env["ALIYUN_OSS_ENDPOINT"]
    ak = env["ALIYUN_ACCESS_KEY_ID"]
    sk = env["ALIYUN_ACCESS_KEY_SECRET"]

    import oss2
    auth = oss2.Auth(ak, sk)
    bucket = oss2.Bucket(auth, f"https://{endpoint}", bucket_name)

    # 1. 设置静态网站托管
    bucket.put_bucket_website(
        oss2.models.BucketWebsite(
            index_file="index.html",
            error_file="index.html",
        )
    )
    print("已开启静态网站托管")

    # 2. 关闭「阻止公共访问」
    bucket.delete_bucket_public_access_block()
    print("已关闭阻止公共访问")

    # 3. 设置 Bucket Policy 允许公开读取
    policy = {
        "Version": "1",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": ["oss:GetObject"],
                "Principal": ["*"],
                "Resource": [f"acs:oss:*:*:{bucket_name}/*"],
            }
        ],
    }
    bucket.put_bucket_policy(json.dumps(policy))
    print("已设置 Bucket Policy 开放读取")

    # 3. 上传静态文件（显式设置 Content-Type 和 Content-Disposition，防止浏览器强制下载）
    content_types = {
        ".html": "text/html; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
    }
    files = [
        ROOT / "index.html",
        ROOT / "config.js",
    ]
    for f in files:
        key = f.name
        headers = {}
        ext = f.suffix
        if ext in content_types:
            headers["Content-Type"] = content_types[ext]
        headers["Content-Disposition"] = "inline"
        bucket.put_object_from_file(key, str(f), headers=headers)
        print(f"已上传: {key}")

    # 3. 对现有 survey-responses 下的文件保持私有（不影响收数）
    # 不需要操作，bucket 本身是私有的，只有显式设为 public-read 的文件才公开

    # 4. 输出访问地址
    site_url = f"https://{bucket_name}.{endpoint}/"
    print(f"\n问卷公网地址: {site_url}")
    return site_url


if __name__ == "__main__":
    main()
