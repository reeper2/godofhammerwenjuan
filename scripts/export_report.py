#!/usr/bin/env python3
"""从 Google 表格导出的 CSV 或 JSON 汇总文件生成简要分析报告。"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd

ENT_LABELS = {
    "large": "大型制造企业",
    "sme": "中小民营企业",
    "trade": "商贸流通企业",
    "other": "其他",
}


def load_submissions(path: Path) -> list[dict]:
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "submissions" in data:
            return data["submissions"]
        if isinstance(data, list):
            return data
        raise ValueError("JSON 格式应为数组或 {submissions: [...]}")

    df = pd.read_csv(path)
    if "raw_json" in df.columns:
        rows = []
        for raw in df["raw_json"].dropna():
            try:
                rows.append(json.loads(raw))
            except json.JSONDecodeError:
                continue
        return rows
    raise ValueError("CSV 需包含 raw_json 列（从 Google 表格导出）")


def build_report(submissions: list[dict], out: Path) -> None:
    n = len(submissions)
    ent = Counter(s.get("entType", "未知") for s in submissions)
    industries = Counter(s.get("industry", "").strip() or "未填" for s in submissions)

    chal_avg: dict[str, float] = {}
    for i in range(1, 9):
        key = f"chal{i}"
        vals = [float(s[key]) for s in submissions if s.get(key)]
        if vals:
            chal_avg[key] = sum(vals) / len(vals)

    lines = [
        "# 问卷数据汇总报告",
        "",
        f"- **有效答卷数**：{n}",
        "",
        "## 企业类型分布",
        "",
    ]
    for k, v in ent.most_common():
        label = ENT_LABELS.get(k, k)
        pct = 100 * v / n if n else 0
        lines.append(f"- {label}：{v} 份（{pct:.1f}%）")

    lines += ["", "## 行业分布（前 10）", ""]
    for ind, v in industries.most_common(10):
        lines.append(f"- {ind}：{v} 份")

    if chal_avg:
        lines += ["", "## 八大挑战维度平均分（1–5）", ""]
        names = [
            "数据治理", "技术基础设施与成本", "安全与合规", "组织与变革",
            "人才能力", "AI应用真实水平", "业财融合与系统孤岛", "投入产出失衡",
        ]
        for i, name in enumerate(names, 1):
            avg = chal_avg.get(f"chal{i}")
            if avg is not None:
                lines.append(f"- {name}：{avg:.2f}")

    lines += [
        "",
        "## 说明",
        "",
        "完整明细请从阿里云 OSS 导出，或使用 fetch_submissions.py 生成的 JSON 做进一步分析。",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"报告已写入: {out.resolve()}（共 {n} 份答卷）")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="CSV（含 raw_json）或 JSON 汇总文件")
    parser.add_argument("-o", "--output", type=Path, default=Path("output/汇总报告.md"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subs = load_submissions(args.input)
    build_report(subs, args.output)


if __name__ == "__main__":
    main()
