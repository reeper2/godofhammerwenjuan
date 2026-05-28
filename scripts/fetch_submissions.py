#!/usr/bin/env python3
"""从阿里云 OSS 下载全部问卷 JSON，合并为 output/survey_results.json"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import oss2
except ImportError:
    print("请先安装：pip3 install oss2", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "survey_results.json"


def load_env() -> dict[str, str]:
    env_path = ROOT / ".env"
    vals: dict[str, str] = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            vals[k.strip()] = v.strip()
    for key in (
        "ALIYUN_OSS_ENDPOINT",
        "ALIYUN_OSS_BUCKET",
        "ALIYUN_ACCESS_KEY_ID",
        "ALIYUN_ACCESS_KEY_SECRET",
        "ALIYUN_OSS_PREFIX",
    ):
        if key not in vals and os.environ.get(key):
            vals[key] = os.environ[key]
    missing = [
        k
        for k in (
            "ALIYUN_OSS_ENDPOINT",
            "ALIYUN_OSS_BUCKET",
            "ALIYUN_ACCESS_KEY_ID",
            "ALIYUN_ACCESS_KEY_SECRET",
        )
        if not vals.get(k)
    ]
    if missing:
        print(f"缺少配置：{', '.join(missing)}", file=sys.stderr)
        print("请复制 .env.example 为 .env 并填写", file=sys.stderr)
        sys.exit(1)
    vals.setdefault("ALIYUN_OSS_PREFIX", "survey-responses/")
    return vals


def get_bucket(cfg: dict[str, str]) -> oss2.Bucket:
    endpoint = cfg["ALIYUN_OSS_ENDPOINT"]
    if not endpoint.startswith("http"):
        endpoint = "https://" + endpoint
    auth = oss2.Auth(cfg["ALIYUN_ACCESS_KEY_ID"], cfg["ALIYUN_ACCESS_KEY_SECRET"])
    return oss2.Bucket(auth, endpoint, cfg["ALIYUN_OSS_BUCKET"])


def fetch_all(cfg: dict[str, str]) -> list[dict]:
    prefix = cfg["ALIYUN_OSS_PREFIX"].lstrip("/")
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    bucket = get_bucket(cfg)
    submissions: list[dict] = []

    for obj in oss2.ObjectIterator(bucket, prefix=prefix):
        if obj.key.endswith("/"):
            continue
        raw = bucket.get_object(obj.key).read()
        try:
            record = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            continue
        payload = record.get("payload")
        if isinstance(payload, dict):
            submissions.append(payload)
        elif isinstance(record, dict):
            submissions.append(record)

    submissions.sort(key=lambda x: x.get("submittedAt", ""), reverse=True)
    # Filter out test submissions (marked by "score" field or "功能测试" name)
    real = [s for s in submissions if not (s.get("score") or "功能测试" in str(s.get("company_name", "")))]
    if len(submissions) != len(real):
        print(f"  ⚠ 已自动排除 {len(submissions) - len(real)} 份测试答卷")
    return real


def main() -> None:
    cfg = load_env()
    submissions = fetch_all(cfg)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(submissions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已从 OSS 导出 {len(submissions)} 份答卷 → {OUT}")


if __name__ == "__main__":
    main()
