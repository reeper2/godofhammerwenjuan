#!/usr/bin/env python3
import json
from pathlib import Path

data = json.loads(Path("output/survey_results.json").read_text())

ent_labels = {"large": "大型制造企业", "sme": "中小民营企业", "trade": "商贸流通企业", "other": "其他"}
tech_map = {
    "tech_ml": "传统机器学习", "tech_llm": "大语言模型", "tech_cv": "计算机视觉",
    "tech_rpa": "RPA+AI", "tech_opt": "智能决策优化", "tech_aigc": "生成式AI",
    "tech_none": "尚未使用任何AI技术", "tech_other": "其他",
}
deploy_map = {
    "deploy_local": "纯本地/私有化部署", "deploy_cloud": "公有云SaaS",
    "deploy_hybrid": "混合部署", "deploy_none": "完全未部署",
}
chal_names = [
    "1.数据治理挑战", "2.技术基础设施与成本", "3.安全与合规",
    "4.组织与变革管理", "5.人才能力", "6.AI应用真实水平",
    "7.业财融合与系统孤岛", "8.投入产出失衡",
]
mat_labels = {"L0": "未开展", "L1": "试点/局部", "L2": "部分覆盖", "L3": "全面集成", "L4": "智能化闭环"}

diag_items = {
    "cert": {
        "cert1": "外部机构不完全认可电子凭证法律效力",
        "cert2": "企业内部系统与外部监管系统不兼容",
        "cert3": "电子发票/回单跨区域互认困难",
        "cert4": "缺乏明确的电子档案保存与审计标准",
    },
    "fusion": {
        "fusion1": "系统独立运行超过5套",
        "fusion2": "人工导出导入数据",
        "fusion3": "接口开发成本高维护困难",
        "fusion4": "集团与子公司系统冲突",
    },
    "cost": {
        "cost1": "Token成本超预期",
        "cost2": "本地化部署投入过高(超100万)",
        "cost3": "云端数据安全顾虑混合部署管理复杂",
        "cost4": "硬件软件更新快刚投入即淘汰",
    },
    "train": {
        "train1": "员工参与过政府补贴培训",
        "train2": "培训认证未用于晋升薪酬",
        "train3": "财务人员缺乏AI操作技能",
        "train4": "招聘复合型人才困难",
    },
    "org": {
        "org1": "管理层关注短期降本",
        "org2": "员工担心替代有抵触情绪",
        "org3": "部门利益冲突数据不愿共享",
        "org4": "缺乏激励考核机制",
    },
    "gov": {
        "gov1": "模型黑箱可解释性差",
        "gov2": "缺乏验证监控机制",
        "gov3": "责任归属不清",
        "gov4": "缺乏伦理准则",
        "gov5": "监管采信标准未建立",
    },
}
diag_names = {
    "cert": "电子凭证与档案应用障碍", "fusion": "业财融合与系统集成问题",
    "cost": "算力与AI成本压力", "train": "人才培养与认证现状",
    "org": "组织与变革阻力来源", "gov": "治理框架挑战",
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
    print("【一、受访企业与人员基本信息】")
    print(f"  职位: {s.get('position', '')}")
    print(f"  企业名称: {s.get('company_name', '') or '未填写'}")
    phone = s.get('phone', '') or s.get('contact_phone', '')
    email = s.get('email', '') or s.get('contact_email', '')
    if phone or email:
        print(f"  联系方式: 电话 {phone}  邮箱 {email}")
    print(f"  行业: {s.get('industry', '')}")
    print(f"  营收: {s.get('revenue', '')}")
    print(f"  员工规模: {s.get('employee_scale', '')}")
    ent = s.get("entType", "")
    print(f"  企业类型: {ent_labels.get(ent, ent)}")

    # Maturity
    mat_keys = sorted(
        [k for k in s if k.startswith("largeTableTable_")],
        key=lambda x: int(x.split("_")[1]),
    )
    if mat_keys:
        print()
        print("【二、AI应用成熟度评估（大型制造企业）】")
        for mk in mat_keys:
            i = int(mk.split("_")[1])
            desc = large_items[i] if i < len(large_items) else mk
            val = s[mk]
            label = mat_labels.get(val, val)
            print(f"  {desc}")
            print(f"    成熟度: {val} ({label})")

    # Tech
    print()
    print("【三、通用AI技术使用情况】")
    tech_selected = [tech_map.get(t, t) for t in s.get("tech", [])]
    print(f"  AI技术形态: {'、'.join(tech_selected) if tech_selected else '未选择'}")
    deploy_selected = [deploy_map.get(d, d) for d in s.get("deploy", [])]
    print(f"  部署方式: {'、'.join(deploy_selected) if deploy_selected else '未选择'}")

    # Challenges
    print()
    print("【四、核心挑战评估 (1=无挑战, 5=严重挑战)】")
    for i in range(1, 9):
        key = f"chal{i}"
        val = s.get(key, "")
        if val:
            print(f"  {chal_names[i - 1]}: {val}")

    # Diagnostics
    print()
    print("【五、专项深度诊断】")
    for g in ["cert", "fusion", "cost", "train", "org", "gov"]:
        selected = [diag_items[g].get(item, item) for item in s.get(g, [])]
        print(f"  {diag_names[g]}: {'；'.join(selected) if selected else '未选择'}")

    # Policy
    print()
    print("【六、政策支持期望】")
    pol_selected = [policy_map.get(p, p) for p in s.get("policies", [])]
    print(f"  政策措施: {'；'.join(pol_selected) if pol_selected else '未选择'}")
    open_c = s.get("open_challenge", "")
    if open_c:
        print(f"  开放问题: {open_c}")

    print()
