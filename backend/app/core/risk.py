"""公共风险等级计算工具。"""


def compute_overall_risk_level(risks: list) -> str:
    """根据风险列表计算总体风险等级。"""
    if any((risk or {}).get("level") == "high" for risk in risks or []):
        return "high"
    if any((risk or {}).get("level") == "medium" for risk in risks or []):
        return "medium"
    return "low"


def compute_overall_score(risks: list) -> int:
    """根据风险列表计算合规评分。"""
    penalty = 0
    for risk in risks or []:
        level = (risk or {}).get("level")
        if level == "high":
            penalty += 25
        elif level == "medium":
            penalty += 12
        else:
            penalty += 5
    return max(20, 100 - penalty)
