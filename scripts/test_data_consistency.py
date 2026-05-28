#!/usr/bin/env python3
"""
Validate that all export/fill scripts stay consistent with the questionnaire HTML structure.
Run this after changing any mapping, the HTML questionnaire, or adding new submission fields.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []

# ── 1. Load the questionnaire HTML and extract expected field names ──────────
html = (ROOT / "调查问卷.html").read_text(encoding="utf-8")

# Extract all radio names, checkbox names, text inputs, textareas
radio_names = set(re.findall(r'<input[^>]*type="radio"[^>]*name="([^"]+)"', html))
checkbox_names = set(re.findall(r'<input[^>]*type="checkbox"[^>]*name="([^"]+)"', html))
text_names = set(re.findall(r'<input[^>]*type="text"[^>]*name="([^"]+)"', html))
textarea_names = set(re.findall(r'<textarea[^>]*name="([^"]+)"', html))

static_field_names = radio_names | checkbox_names | text_names | textarea_names

# ── 2. Extract dynamic table definitions (buildTable calls) ──────────────────
table_ids = re.findall(r'buildTable\("([^"]+)",', html)
table_item_counts = {}
for data_var_name, tid in [("large", "largeTableTable"), ("sme", "smeTableTable"), ("trade", "tradeTableTable")]:
    obj_match = re.search(
        rf'const {data_var_name}Data\s*=\s*\{{.*?rows:\s*\[(.*?)\]\s*\}};', html, re.DOTALL
    )
    if obj_match:
        rows_block = obj_match.group(1)
        items_arrays = re.findall(r'items:\s*\[(.*?)\]', rows_block, re.DOTALL)
        total = 0
        for arr in items_arrays:
            total += len(re.findall(r'"([^"]+)"', arr))
        table_item_counts[tid] = total

# ── 3. Load a real submission and check key consistency ──────────────────────
results_path = ROOT / "output" / "survey_results.json"
if results_path.exists():
    submissions = json.loads(results_path.read_text())
    for si, sub in enumerate(submissions):
        for key in sub:
            # Skip metadata
            if key in ("submittedAt", "score", "feedback"):
                continue
            # Dynamic table keys: {tableId}_{index}
            if re.match(r'^(largeTableTable|smeTableTable|tradeTableTable)_\d+$', key):
                tid = key.rsplit("_", 1)[0]
                idx = int(key.rsplit("_", 1)[1])
                expected_count = table_item_counts.get(tid, 0)
                if idx >= expected_count:
                    errors.append(
                        f"  submission[{si}] key '{key}' idx={idx} exceeds expected "
                        f"count={expected_count} for {tid}"
                    )
                continue
            # Challenge keys
            if re.match(r'^chal[1-8]$', key):
                continue
            # Array fields (checkbox groups)
            if isinstance(sub[key], list):
                for item in sub[key]:
                    if item not in checkbox_names and item != "policy_other":
                        errors.append(
                            f"  submission[{si}] '{key}' contains '{item}' "
                            f"which is not a known checkbox name in the HTML"
                        )
                continue
            # Scalar fields
            if isinstance(sub[key], str) and sub[key]:
                if key not in static_field_names and key not in (
                    "position_other", "tech_other_text", "cert_other_text",
                    "fusion_other_text", "cost_other_text", "train_other_text",
                    "org_other_text", "gov_other_text", "policy_other_text",
                    "contact_name", "contact_phone", "contact_email",
                    "company_name", "industry", "phone", "email",
                ):
                    errors.append(
                        f"  submission[{si}] unknown field '{key}' = '{sub[key][:50]}'"
                    )

# ── 4. Verify print_details.py mapping covers all submission keys ────────────
print_script = (ROOT / "scripts" / "print_details.py").read_text()
for si, sub in enumerate(submissions):
    for key in sub:
        if key in ("submittedAt", "score", "feedback"):
            continue
        if re.match(r'^(largeTableTable|smeTableTable|tradeTableTable)_\d+$', key):
            continue
        if re.match(r'^chal[1-8]$', key):
            continue
        if key in ("tech_other_text", "policy_other_text", "open_challenge",
                   "position_other", "contact_name", "contact_phone", "contact_email"):
            continue
        if key not in print_script:
            errors.append(f"  print_details.py does not reference submission key '{key}'")

# ── 5. Verify fill_and_export.py references all field types ──────────────────
fill_script = (ROOT / "scripts" / "fill_and_export.py").read_text()
expected_refs = ["position", "revenue", "employee_scale", "entType",
                 "tech", "deploy", "cert", "fusion", "cost", "train", "org", "gov",
                 "policies", "open_challenge", "contact_name", "contact_phone", "contact_email"]
for ref in expected_refs:
    if ref not in fill_script:
        errors.append(f"  fill_and_export.py missing reference to '{ref}'")
# chal1-chal8 are referenced dynamically as 'chal' + i in a loop
if "chal" not in fill_script:
    errors.append("  fill_and_export.py missing challenge field references")

# ── 6. Report ────────────────────────────────────────────────────────────────
if errors:
    print("❌ 数据一致性检查失败：")
    for e in errors:
        print(e)
    sys.exit(1)
else:
    print("✅ 数据一致性检查通过")
    print(f"   静态字段: {len(static_field_names)} 个")
    print(f"   动态表格: {table_item_counts}")
    print(f"   本地答卷: {len(submissions)} 份")
