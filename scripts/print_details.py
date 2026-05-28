#!/usr/bin/env python3
import json
from pathlib import Path

data = json.loads(Path("output/survey_results.json").read_text())

ent_labels = {"large": "大型制造企业", "sme": "中小民营企业", "trade": "商贸流通企业", "other": "其他"}

# Maps for new fields
fin_tool_map = {
    'fin_ai_tool_1': '智能核算类', 'fin_ai_tool_2': '智能审核类', 'fin_ai_tool_3': '智能报表类',
    'fin_ai_tool_4': '智能风控类', 'fin_ai_tool_5': '智能税务类', 'fin_ai_tool_6': '智能资金类',
    'fin_ai_tool_7': 'AI数据分析类', 'fin_ai_tool_8': '智能RPA自动化', 'fin_ai_tool_none': '暂未使用任何财务AI工具',
    'fin_ai_tool_other': '其他'
}
fin_scene_map = {
    'fin_scene_1': '账务核算', 'fin_scene_2': '费用报销', 'fin_scene_3': '税务管理',
    'fin_scene_4': '资金管理', 'fin_scene_5': '成本管理', 'fin_scene_6': '风控合规',
    'fin_scene_7': '经营分析', 'fin_scene_8': '预算管理', 'fin_scene_other': '其他'
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
    'invest_dir1': 'AI财务系统采购、升级与运维', 'invest_dir2': 'RPA机器人、智能工具定制开发',
    'invest_dir3': '财务数据治理、数据中台搭建', 'invest_dir4': '外部咨询、方案规划与落地服务',
    'invest_dir5': '财务人员AI技能培训', 'invest_dir_other': '其他'
}
future_scene_map = {
    'future_scene1': '全流程智能税务管理', 'future_scene2': '现金流智能预测与资金管控',
    'future_scene3': '财务RPA全流程自动化', 'future_scene4': '智能预算与成本管控',
    'future_scene5': '财务AI经营分析与决策系统', 'future_scene6': '内控风控智能预警平台',
    'future_scene_other': '其他'
}
future_invest_map = {
    'future_invest1': '系统升级与智能化改造', 'future_invest2': '企业财务数据治理',
    'future_invest3': '数智化财务人才培养与引进', 'future_invest4': '外部专业咨询与方案落地',
    'future_invest5': '安全合规体系建设'
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

large_items = [
    "A1.1 预算编制自动化：基于历史财务数据与业务驱动因素自动生成年度预算草案",
    "A1.2 滚动预测：AI模型每月/每季度自动更新未来3-6个月收入、成本及利润预测",
    "A1.3 预实差异分析：自动对比预算与实际执行数据，识别异常波动并推送归因分析",
    "A1.4 情景模拟：支持假设分析(如原材料涨价20%)并输出财务结果",
    "A2.1 研发目标成本模拟：设计阶段根据BOM自动估算制造成本并预警超预算风险",
    "A2.2 采购价格预测与供应商选择：基于大宗商品行情与历史价格推荐采购时机及供应商",
    "A2.3 生产成本实时监控：对接MES系统实时归集料、工、费，发现异常自动预警",
    "A2.4 物流与售后成本优化：分析运输、仓储、售后维修成本并提供降本建议",
    "A3.1 销售预测驱动计划：利用历史销售与市场趋势自动触发生产排产与采购补货",
    "A3.2 智能库存调配：多工厂/多仓库间动态平衡库存，降低总库存水平并防止缺货",
    "A3.3 质量检测与预测性维护：AI视觉检测缺陷，IoT数据预测设备故障以减少停机",
]

for idx, s in enumerate(data):
    sep = "=" * 60
    print(sep)
    print(f"  答 卷 {idx + 1}")
    print(sep)
    print(f"提交时间: {s.get('submittedAt', '')}")
    print()

    # Basic info
    print("【一、企业与填写人基本信息】")
    print(f"  职位: {s.get('position', '')} {s.get('position_other', '')}")
    print(f"  企业名称: {s.get('company_name', '') or '未填写'}")
    phone = s.get('phone', '') or s.get('contact_phone', '')
    email = s.get('email', '') or s.get('contact_email', '')
    if phone or email:
        print(f"  联系方式: 电话 {phone}  邮箱 {email}")
    ind = s.get('industry', '')
    ind_other = s.get('industry_other_text', '')
    print(f"  行业: {ind} {ind_other and '('+ind_other+')' or ''}")
    print(f"  企业规模: {s.get('scale', '')}")
    print(f"  营收: {s.get('revenue', '')}")
    print(f"  员工规模: {s.get('employee_scale', '')}")
    print(f"  财务信息化年限: {s.get('it_years', '')}")
    ent = s.get("entType", "")
    print(f"  企业类型: {ent_labels.get(ent, ent)}")

    # Financial AI application status
    print()
    print("【二、企业财务AI应用现状与成熟度】")
    tools = [fin_tool_map.get(t, t) for t in s.get("fin_ai_tools", [])]
    if s.get("fin_ai_tool_other_text"):
        tools.append(f"其他: {s['fin_ai_tool_other_text']}")
    print(f"  财务AI工具类型: {'、'.join(tools) if tools else '未选择'}")
    scenes = [fin_scene_map.get(t, t) for t in s.get("fin_scenes", [])]
    if s.get("fin_scene_other_text"):
        scenes.append(f"其他: {s['fin_scene_other_text']}")
    print(f"  落地场景: {'、'.join(scenes) if scenes else '未选择'}")
    print(f"  整体应用程度: {s.get('fin_overall_level', '')}")
    tech_selected = [tech_map.get(t, t) for t in s.get("tech", [])]
    if s.get("tech_other_text"):
        tech_selected.append(f"其他: {s['tech_other_text']}")
    print(f"  AI技术形态: {'、'.join(tech_selected) if tech_selected else '未选择'}")
    deploy_selected = [deploy_map.get(d, d) for d in s.get("deploy", [])]
    print(f"  部署方式: {'、'.join(deploy_selected) if deploy_selected else '未选择'}")

    # Maturity
    mat_keys = sorted(
        [k for k in s if k.startswith("largeTableTable_") or k.startswith("smeTableTable_") or k.startswith("tradeTableTable_")],
        key=lambda x: int(x.split("_")[1]),
    )
    if mat_keys:
        print()
        print("【AI应用成熟度评估】")
        for mk in mat_keys:
            val = s[mk]
            label = mat_labels.get(val, val)
            print(f"  {mk}: {val} ({label})")

    # Investment
    print()
    print("【三、财务AI转型投入与人才配置】")
    print(f"  近一年专项投入: {s.get('budget', '未填写')}")
    invests = [invest_dir_map.get(t, t) for t in s.get("invest_dir", [])]
    if s.get("invest_dir_other_text"):
        invests.append(f"其他: {s['invest_dir_other_text']}")
    print(f"  投入方向: {'、'.join(invests) if invests else '未选择'}")
    print(f"  专职人力配置: {s.get('staff_ai', '未填写')}")
    print(f"  财务团队AI技能水平: {s.get('skill_level', '未填写')}")

    # Challenges
    print()
    print("【四、挑战评估 (1=无挑战, 5=严重挑战)】")
    print("  数字化转型挑战:")
    for i in range(1, 9):
        key = f"chal{i}"
        val = s.get(key, "")
        if val:
            print(f"    {chal_names[i - 1]}: {val}")
    print("  AI赋能专项挑战:")
    for i in range(1, 7):
        key = f"echal{i}"
        val = s.get(key, "")
        if val:
            print(f"    {echal_names[i - 1]}: {val}")

    # Benefits
    print()
    print("【五、财务AI转型成效评估 (1=无提升, 5=大幅提升)】")
    for i in range(1, 6):
        key = f"benefit{i}"
        val = s.get(key, "")
        if val:
            print(f"  {benefit_names[i - 1]}: {val}")

    # Future plans
    print()
    print("【六、未来转型计划】")
    print(f"  整体规划: {s.get('future_plan', '未填写')}")
    fscenes = [future_scene_map.get(t, t) for t in s.get("future_scenes", [])]
    if s.get("future_scene_other_text"):
        fscenes.append(f"其他: {s['future_scene_other_text']}")
    print(f"  优先落地场景: {'、'.join(fscenes) if fscenes else '未选择'}")
    finvests = [future_invest_map.get(t, t) for t in s.get("future_invest", [])]
    print(f"  核心投入方向: {'、'.join(finvests) if finvests else '未选择'}")

    # Policy
    print()
    print("【七、政策支持期望与开放建议】")
    pol_selected = [policy_map.get(p, p) for p in s.get("policies", [])]
    if s.get("policy_other_text"):
        pol_selected.append(f"其他: {s['policy_other_text']}")
    print(f"  政策措施: {'、'.join(pol_selected) if pol_selected else '未选择'}")
    core_pain = s.get("core_pain", "")
    if core_pain:
        print(f"  核心痛点: {core_pain}")
    advice = s.get("advice", "")
    if advice:
        print(f"  建议: {advice}")
    open_c = s.get("open_challenge", "")
    if open_c:
        print(f"  开放问题: {open_c}")

    print()
