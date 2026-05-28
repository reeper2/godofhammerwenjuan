#!/usr/bin/env python3
"""从 LeanCloud 拉取全部答卷，保存为 output/survey_results.json"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    print("请先安装：pip3 install requests", file=sys.stderr)
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
        "LEANCLOUD_APP_ID",
        "LEANCLOUD_MASTER_KEY",
        "LEANCLOUD_API_SERVER",
        "LEANCLOUD_CLASS",
    ):
        if key not in vals and os.environ.get(key):
            vals[key] = os.environ[key]
    missing = [k for k in ("LEANCLOUD_APP_ID", "LEANCLOUD_MASTER_KEY", "LEANCLOUD_API_SERVER") if not vals.get(k)]
    if missing:
        print(f"缺少配置：{', '.join(missing)}", file=sys.stderr)
        print("请复制 .env.example 为 .env 并填写 Master Key 等", file=sys.stderr)
        sys.exit(1)
    vals.setdefault("LEANCLOUD_CLASS", "SurveyResponse")
    return vals


def fetch_all(cfg: dict[str, str]) -> list[dict]:
    base = cfg["LEANCLOUD_API_SERVER"].rstrip("/")
    cls = cfg["LEANCLOUD_CLASS"]
    url = f"{base}/1.1/classes/{cls}"
    headers = {
        "X-LC-Id": cfg["LEANCLOUD_APP_ID"],
        "X-LC-Key": cfg["LEANCLOUD_MASTER_KEY"],
        "Content-Type": "application/json",
    }
    all_rows: list[dict] = []
    skip = 0
    while True:
        r = requests.get(
            url,
            headers=headers,
            params={"limit": 100, "skip": skip, "order": "-createdAt"},
            timeout=30,
        )
        r.raise_for_status()
        batch = r.json().get("results", [])
        if not batch:
            break
        all_rows.extend(batch)
        if len(batch) < 100:
            break
        skip += 100
    return all_rows


def main() -> None:
    cfg = load_env()
    rows = fetch_all(cfg)
    submissions = []
    for row in rows:
        if isinstance(row.get("payload"), dict):
            submissions.append(row["payload"])
        else:
            submissions.append(row)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(submissions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"已导出 {len(submissions)} 份答卷 → {OUT}")


if __name__ == "__main__":
    main()
