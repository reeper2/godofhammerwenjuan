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
var texts = ['company_name','industry','phone','email','tech_other_text',
  'cert_other_text','fusion_other_text','cost_other_text',
  'train_other_text','org_other_text','gov_other_text',
  'policy_other_text','contact_name','contact_phone','contact_email'];
texts.forEach(function(n) {{
  var e = document.querySelector('[name="' + n + '"]');
  if (e && data[n]) e.value = data[n];
}});

// Textarea
var ta = document.querySelector('[name="open_challenge"]');
if (ta && data.open_challenge) ta.value = data.open_challenge;

// Radio buttons
['position','revenue','employee_scale'].forEach(function(n) {{
  if (data[n]) {{
    var r = document.querySelector('[name="' + n + '"][value="' + data[n].replace(/"/g,'\\\\"') + '"]');
    if (r) r.checked = true;
  }}
}});

// entType
if (data.entType) {{
  var r = document.querySelector('[name="entType"][value="' + data.entType + '"]');
  if (r) r.checked = true;
}}

// Checkbox groups
['tech','deploy','cert','fusion','cost','train','org','gov'].forEach(function(g) {{
  (data[g] || []).forEach(function(n) {{
    var c = document.querySelector('[name="' + n + '"]');
    if (c) c.checked = true;
  }});
}});

// Challenges
for (var i = 1; i <= 8; i++) {{
  var v = data['chal' + i];
  if (v) {{
    var r = document.querySelector('[name="chal' + i + '"][value="' + v + '"]');
    if (r) r.checked = true;
  }}
}}

// Policies
(data.policies || []).forEach(function(n) {{
  var c = document.querySelector('[name="' + n + '"]');
  if (c) c.checked = true;
}});

// Maturity table — derive prefix from entType to match buildTable() naming
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
