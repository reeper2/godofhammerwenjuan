#!/usr/bin/env python3
"""Take the original questionnaire HTML and pre-fill it with submission data.
Output: 问卷_{YYMMDDHHmm}.html — strictly matches the original HTML form."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_SRC = ROOT / "调查问卷.html"
DATA_JSON = ROOT / "output" / "survey_results.json"

submissions = json.loads(DATA_JSON.read_text())

def is_test(sub):
    return bool(sub.get("score")) or "功能测试" in str(sub.get("company_name", ""))

real = [s for s in submissions if not is_test(s)]
if not real:
    print("没有有效答卷可导出")
    exit(1)
if len(submissions) != len(real):
    print(f"  ⚠ 已自动排除 {len(submissions) - len(real)} 份测试答卷，导出 {len(real)} 份")

for sub in real:
    ts = sub.get("submittedAt", "")
    filename = "无效时间"
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        bj = dt.astimezone(timezone(timedelta(hours=8)))
        filename = bj.strftime("问卷_%y%m%d%H%M")
    except (ValueError, TypeError):
        pass
    out = ROOT / "output" / f"{filename}.html"

    html = HTML_SRC.read_text(encoding="utf-8")

    fill_script = f"""
<script>
(function() {{
var data = {json.dumps(sub, ensure_ascii=False)};

// Text inputs
var texts = ['company_name','phone','email','contact_name','contact_phone','contact_email',
  'position_other','industry_other_text',  'fin_ai_tool_other_text',
  'tech_other_text','invest_dir_other_text','future_scene_other_text','policy_other_text'];
texts.forEach(function(n) {{
  var e = document.querySelector('[name="' + n + '"]');
  if (e && data[n]) e.value = data[n];
}});

// Textarea
['core_pain','advice','open_challenge'].forEach(function(n) {{
  var e = document.querySelector('[name="' + n + '"]');
  if (e && data[n]) e.value = data[n];
}});

// Radio buttons (single choice)
['position','industry','scale','revenue','employee_scale','it_years','entType',
 'fin_overall_level','staff_ai','skill_level','future_plan'].forEach(function(n) {{
  if (data[n]) {{
    var r = document.querySelector('[name="' + n + '"][value="' + data[n].replace(/"/g,'\\\\"') + '"]');
    if (r) r.checked = true;
  }}
}});

// Checkbox groups
['fin_ai_tools','tech','deploy','invest_dir','future_scenes','future_invest','policies'].forEach(function(g) {{
  (data[g] || []).forEach(function(n) {{
    var c = document.querySelector('[name="' + n + '"]');
    if (c) c.checked = true;
  }});
}});

// Challenge ratings (chal1-8, echal1-6, benefit1-5)
for (var i = 1; i <= 8; i++) {{
  var v = data['chal' + i];
  if (v) {{
    var r = document.querySelector('[name="chal' + i + '"][value="' + v + '"]');
    if (r) r.checked = true;
  }}
}}
for (var i = 1; i <= 6; i++) {{
  var v = data['echal' + i];
  if (v) {{
    var r = document.querySelector('[name="echal' + i + '"][value="' + v + '"]');
    if (r) r.checked = true;
  }}
}}
for (var i = 1; i <= 5; i++) {{
  var v = data['benefit' + i];
  if (v) {{
    var r = document.querySelector('[name="benefit' + i + '"][value="' + v + '"]');
    if (r) r.checked = true;
  }}
}}

// Maturity table
if (data.entType) {{
  var prefix = data.entType + 'TableTable';
  Object.keys(data).filter(function(k) {{ return k.startsWith(prefix + '_'); }})
    .forEach(function(k) {{
      var r = document.querySelector('[name="' + k + '"][value="' + data[k] + '"]');
      if (r) r.checked = true;
  }});
  // Show the correct table
  var tbls = {{'large':'largeTable','sme':'smeTable','trade':'tradeTable'}};
  var showId = tbls[data.entType];
  Object.values(tbls).forEach(function(id) {{
    var el = document.getElementById(id);
    if (el) el.classList[id === showId ? 'remove' : 'add']('hidden-section');
  }});
}}

// Lock all fields so answers cannot be changed
document.querySelectorAll('input').forEach(function(el) {{ el.disabled = true; }});
document.querySelectorAll('textarea').forEach(function(el) {{ el.readOnly = true; }});
document.getElementById('submitBtn').disabled = true;
}})();
</script>
"""

    html = html.replace("</body>", fill_script + "\n</body>")
    out.write_text(html, encoding="utf-8")
    print(f"已生成: {out.resolve()}")
