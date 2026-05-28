#!/usr/bin/env python3
import json
import re
from pathlib import Path

data = json.loads(Path("output/survey_results.json").read_text())

ent_labels = {"large": "大型制造企业", "sme": "中小民营企业", "trade": "商贸流通企业", "other": "其他"}
fin_tool_map = {
    "fin_ai_tool_1": "智能核算类", "fin_ai_tool_2": "智能审核类", "fin_ai_tool_3": "智能报表类",
    "fin_ai_tool_4": "智能风控类", "fin_ai_tool_5": "智能税务类", "fin_ai_tool_6": "智能资金类",
    "fin_ai_tool_7": "AI数据分析类", "fin_ai_tool_8": "智能RPA自动化",
    "fin_ai_tool_none": "暂未使用任何财务AI工具", "fin_ai_tool_other": "其他",
}
fin_scene_map = {
    "fin_scene_1": "账务核算", "fin_scene_2": "费用报销", "fin_scene_3": "税务管理",
    "fin_scene_4": "资金管理", "fin_scene_5": "成本管理", "fin_scene_6": "风控合规",
    "fin_scene_7": "经营分析", "fin_scene_8": "预算管理", "fin_scene_other": "其他",
}
tech_map = {
    "tech_ml": "传统机器学习", "tech_llm": "大语言模型", "tech_cv": "计算机视觉",
    "tech_rpa": "RPA+AI", "tech_opt": "智能决策优化", "tech_aigc": "生成式AI",
    "tech_none": "尚未使用任何AI技术", "tech_other": "其他",
}
deploy_map = {
    "deploy_local": "纯本地/私有化部署", "deploy_cloud": "公有云SaaS",
    "deploy_hybrid": "混合部署", "deploy_none": "完全未部署",
}
invest_dir_map = {
    "invest_dir1": "AI财务系统采购、升级与运维", "invest_dir2": "RPA机器人、智能工具定制开发",
    "invest_dir3": "财务数据治理、数据中台搭建", "invest_dir4": "外部咨询、方案规划与落地服务",
    "invest_dir5": "财务人员AI技能培训", "invest_dir_other": "其他",
}
chal_names = [
    "1.数据治理挑战", "2.技术基础设施与成本", "3.安全与合规",
    "4.组织与变革管理", "5.人才能力", "6.AI应用真实水平",
    "7.业财融合与系统孤岛", "8.投入产出失衡",
]
echal_names = [
    "1.技术层面", "2.成本层面", "3.人才层面",
    "4.管理层面", "5.风险合规层面", "6.落地价值层面",
]
benefit_names = [
    "1.效率提升", "2.成本降低", "3.风险控制",
    "4.决策赋能", "5.合规水平",
]
mat_labels = {"L0": "未开展", "L1": "试点/局部", "L2": "部分覆盖", "L3": "全面集成", "L4": "智能化闭环"}

future_scene_map = {
    "future_scene1": "全流程智能税务管理", "future_scene2": "现金流智能预测与资金管控",
    "future_scene3": "财务RPA全流程自动化", "future_scene4": "智能预算与成本管控",
    "future_scene5": "财务AI经营分析与决策系统", "future_scene6": "内控风控智能预警平台",
}
future_invest_map = {
    "future_invest1": "系统升级与智能化改造", "future_invest2": "企业财务数据治理",
    "future_invest3": "数智化财务人才培养与引进", "future_invest4": "外部专业咨询与方案落地",
    "future_invest5": "安全合规体系建设",
}
policy_map = {
    "policy1": "推动电子凭证全国统一法律效力",
    "policy2": "建设国家级标杆案例库",
    "policy3": "对中小企业财政补贴或税收减免",
    "policy4": "建设区域性AI算力共享中心",
    "policy5": "纳入国家职业资格体系",
    "policy6": "制定AI合规指引与审计标准",
    "policy7": "建立财税数据互通标准化接口",
    "policy8": "设立专项贷款或风险补偿基金",
    "policy9": "组织行业培训与供需对接",
}

for idx, s in enumerate(data):
    sep = "=" * 60
    print(sep)
    print(f"  答 卷 {idx + 1}")
    print(sep)
    print(f"提交时间: {s.get('submittedAt', '')}")
    print()

    # Basic info
    print("【一、受访企业与人员基本信息】")
    print(f"  职位: {s.get('position', '')}")
    print(f"  企业名称: {s.get('company_name', '') or '未填写'}")
    phone = s.get('phone', '') or s.get('contact_phone', '')
    email = s.get('email', '') or s.get('contact_email', '')
    if phone or email:
        print(f"  联系方式: 电话 {phone}  邮箱 {email}")
    print(f"  行业: {s.get('industry', '')}")
    print(f"  企业规模: {s.get('scale', '')}")
    print(f"  营收: {s.get('revenue', '')}")
    print(f"  员工规模: {s.get('employee_scale', '')}")
    print(f"  财务信息化年限: {s.get('it_years', '')}")
    ent = s.get("entType", "")
    print(f"  企业类型: {ent_labels.get(ent, ent)}")

    # FinAI application
    print()
    print("【二、财务AI应用现状与成熟度】")
    tools = [fin_tool_map.get(t, t) for t in s.get("fin_ai_tools", [])]
    print(f"  财务AI工具类型: {'、'.join(tools) if tools else '未选择'}")
    scenes = [fin_scene_map.get(sc, sc) for sc in s.get("fin_scenes", [])]
    print(f"  财务AI落地场景: {'、'.join(scenes) if scenes else '未选择'}")
    print(f"  财务AI整体应用程度: {s.get('fin_overall_level', '')}")
    techs = [tech_map.get(t, t) for t in s.get("tech", [])]
    print(f"  通用AI技术形态: {'、'.join(techs) if techs else '未选择'}")
    deploys = [deploy_map.get(d, d) for d in s.get("deploy", [])]
    print(f"  部署方式: {'、'.join(deploys) if deploys else '未选择'}")

    # Maturity (dynamic tables)
    mat_keys = sorted(
        [k for k in s if re.match(r'^(largeTableTable|smeTableTable|tradeTableTable)_\d+$', k)],
        key=lambda x: (x.rsplit("_", 1)[0], int(x.rsplit("_", 1)[1])),
    )
    if mat_keys:
        print(f"  AI成熟度评估（{len(mat_keys)}项）:")
        for mk in mat_keys:
            val = s[mk]
            label = mat_labels.get(val, val)
            print(f"    {mk}: {val} ({label})")

    # Investment & talent
    print()
    print("【三、财务AI转型投入与人才配置】")
    print(f"  近一年专项预算: {s.get('budget', '')}")
    invests = [invest_dir_map.get(i, i) for i in s.get("invest_dir", [])]
    print(f"  投入主要方向: {'、'.join(invests) if invests else '未选择'}")
    print(f"  专职人力配置: {s.get('staff_ai', '')}")
    print(f"  团队AI技能水平: {s.get('skill_level', '')}")

    # Challenges (basic + AI-specific)
    print()
    print("【四、挑战评估】")
    for i in range(1, 9):
        key = f"chal{i}"
        val = s.get(key, "")
        if val:
            print(f"  {chal_names[i - 1]}: {val}")
    any_echal = any(s.get(f"echal{i}", "") for i in range(1, 7))
    if any_echal:
        print("  --- AI赋能专项挑战 ---")
        for i in range(1, 7):
            key = f"echal{i}"
            val = s.get(key, "")
            if val:
                print(f"  {echal_names[i - 1]}: {val}")

    # Benefits
    any_ben = any(s.get(f"benefit{i}", "") for i in range(1, 6))
    if any_ben:
        print()
        print("【五、财务AI转型落地成效】")
        for i in range(1, 6):
            key = f"benefit{i}"
            val = s.get(key, "")
            if val:
                print(f"  {benefit_names[i - 1]}: {val}")

    # Future plans
    future_plan = s.get("future_plan", "")
    future_scenes = s.get("future_scenes", [])
    future_invest = s.get("future_invest", [])
    if future_plan or future_scenes or future_invest:
        print()
        print("【六、未来转型计划】")
        print(f"  整体规划: {future_plan or '未填写'}")
        fs = [future_scene_map.get(f, f) for f in future_scenes]
        print(f"  优先落地场景: {'、'.join(fs) if fs else '未选择'}")
        fi = [future_invest_map.get(f, f) for f in future_invest]
        print(f"  核心投入方向: {'、'.join(fi) if fi else '未选择'}")

    # Policy & open questions
    print()
    print("【七、政策支持与开放建议】")
    pol = [policy_map.get(p, p) for p in s.get("policies", [])]
    print(f"  政策措施: {'、'.join(pol) if pol else '未选择'}")
    core_pain = s.get("core_pain", "")
    if core_pain:
        print(f"  核心痛点: {core_pain}")
    advice = s.get("advice", "")
    if advice:
        print(f"  工具/政策建议: {advice}")
    open_c = s.get("open_challenge", "")
    if open_c:
        print(f"  其他开放问题: {open_c}")

    print()
