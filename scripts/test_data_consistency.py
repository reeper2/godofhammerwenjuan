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

# ── 2. Extract dynamic table definitions (buildDynamicTable calls) ──────────
table_ids = re.findall(r'buildDynamicTable\("([^"]+)",', html)
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
            if key in ("submittedAt", "score", "feedback"):
                continue
            if re.match(r'^(largeTableTable|smeTableTable|tradeTableTable)_\d+$', key):
                tid = key.rsplit("_", 1)[0]
                idx = int(key.rsplit("_", 1)[1])
                expected_count = table_item_counts.get(tid, 0)
                if idx >= expected_count:
                    errors.append(
                        f"  submission[{si}] key '{key}' idx={idx} exceeds expected "
                        f"count={expected_count} for {expected_tid}"
                    )
                continue
            if re.match(r'^chal[1-8]$', key) or re.match(r'^echal[1-6]$', key) or re.match(r'^benefit[1-5]$', key):
                continue
            if isinstance(sub[key], list):
                for item in sub[key]:
                    if item not in checkbox_names and item != "policy_other":
                        errors.append(
                            f"  submission[{si}] '{key}' contains '{item}' "
                            f"which is not a known checkbox name in the HTML"
                        )
                continue
            if isinstance(sub[key], str) and sub[key]:
                if key not in static_field_names and key not in (
                    "position_other", "industry_other_text", "fin_ai_tool_other_text",
                    "fin_scene_other_text", "tech_other_text", "invest_dir_other_text",
                    "future_scene_other_text", "policy_other_text",
                    "contact_name", "contact_phone", "contact_email",
                    "company_name", "phone", "email",
                ):
                    errors.append(
                        f"  submission[{si}] unknown field '{key}' = '{sub[key][:50]}'"
                    )

# ── 4. Verify print_details.py mapping covers all submission keys ────────────
print_script = (ROOT / "scripts" / "print_details.py").read_text()
if results_path.exists():
    for si, sub in enumerate(submissions):
        for key in sub:
            if key in ("submittedAt", "score", "feedback"):
                continue
            if re.match(r'^(largeTableTable|smeTableTable|tradeTableTable)_\d+$', key):
                continue
            if re.match(r'^chal[1-8]$', key) or re.match(r'^echal[1-6]$', key) or re.match(r'^benefit[1-5]$', key):
                continue
            if key in ("tech_other_text", "policy_other_text", "open_challenge",
                       "position_other", "industry_other_text", "fin_ai_tool_other_text",
                       "fin_scene_other_text", "invest_dir_other_text", "future_scene_other_text",
                       "contact_name", "contact_phone", "contact_email"):
                continue
            if key not in print_script:
                errors.append(f"  print_details.py does not reference submission key '{key}'")
else:
    print("  (无本地答卷数据，跳过 print_details.py 键覆盖检查)")

# ── 5. Verify fill_and_export.py references all field types ──────────────────
fill_script = (ROOT / "scripts" / "fill_and_export.py").read_text()
expected_refs = ["position", "industry", "scale", "revenue", "employee_scale", "it_years", "entType",
                 "fin_ai_tools", "fin_scenes", "fin_overall_level",
                 "tech", "deploy", "invest_dir", "staff_ai", "skill_level",
                 "future_plan", "future_scenes", "future_invest",
                 "policies", "core_pain", "advice", "open_challenge",
                 "contact_name", "contact_phone", "contact_email"]
for ref in expected_refs:
    if ref not in fill_script:
        errors.append(f"  fill_and_export.py missing reference to '{ref}'")
# chal/echal/benefit are referenced dynamically as prefix + i in loops
if "chal" not in fill_script:
    errors.append("  fill_and_export.py missing challenge field references")
if "echal" not in fill_script:
    errors.append("  fill_and_export.py missing e-challenge field references")
if "benefit" not in fill_script:
    errors.append("  fill_and_export.py missing benefit field references")

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
    if results_path.exists():
        print(f"   本地答卷: {len(submissions)} 份")
