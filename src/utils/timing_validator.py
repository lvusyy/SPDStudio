"""
DDR4 时序参数验证器
基于 JEDEC DDR4 规范 (JESD79-4C)
"""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class RiskLevel(Enum):
    """风险等级"""
    SAFE = "safe"       # 绿色 - 在 JEDEC 规范内
    WARNING = "warning" # 黄色 - 低于推荐值
    DANGER = "danger"   # 红色 - 显著低于规范


@dataclass
class TimingLimit:
    """时序限制"""
    name: str
    unit: str
    jedec_min: float
    warning_threshold: float
    danger_threshold: float
    description_zh: str


# JEDEC DDR4 时序限制（基于 JESD79-4C 规范）
TIMING_LIMITS = {
    "tCK": TimingLimit(
        "tCK", "ns", 0.625, 0.500, 0.417,
        "时钟周期过短可能导致内存不稳定"
    ),
    "tAA": TimingLimit(
        "tAA", "ns", 12.5, 10.0, 8.0,
        "CAS 延迟过低可能导致数据错误"
    ),
    "tRCD": TimingLimit(
        "tRCD", "ns", 12.5, 10.0, 8.0,
        "RAS 到 CAS 延迟过低可能导致行访问错误"
    ),
    "tRP": TimingLimit(
        "tRP", "ns", 12.5, 10.0, 8.0,
        "行预充电时间过短可能导致行冲突"
    ),
    "tRAS": TimingLimit(
        "tRAS", "ns", 32.0, 28.0, 24.0,
        "激活到预充电时间过短可能导致数据丢失"
    ),
    "tRC": TimingLimit(
        "tRC", "ns", 45.0, 40.0, 35.0,
        "行周期时间过短可能导致时序冲突"
    ),
    "tRFC1": TimingLimit(
        "tRFC1", "ns", 350.0, 280.0, 175.0,
        "刷新恢复时间过短会导致数据丢失"
    ),
}


# 风险等级对应的颜色
RISK_COLORS = {
    RiskLevel.SAFE: "#27ae60",    # Green
    RiskLevel.WARNING: "#f39c12", # Yellow/Orange
    RiskLevel.DANGER: "#c0392b",  # Red
}


def validate_timing(param_name: str, value_ns: float) -> Tuple[RiskLevel, str]:
    """
    验证时序参数值

    Args:
        param_name: 参数名称 (tCK, tAA, tRCD, tRP, tRAS, tRC, tRFC1)
        value_ns: 参数值（纳秒）

    Returns:
        (风险等级, 警告消息)
    """
    limit = TIMING_LIMITS.get(param_name)
    if not limit:
        return (RiskLevel.SAFE, "")

    if value_ns < limit.danger_threshold:
        return (
            RiskLevel.DANGER,
            f"⚠️ 危险: {limit.description_zh}\n"
            f"当前值 {value_ns:.3f}{limit.unit} 远低于安全阈值 {limit.jedec_min}{limit.unit}"
        )
    elif value_ns < limit.warning_threshold:
        return (
            RiskLevel.WARNING,
            f"⚡ 警告: {limit.description_zh}\n"
            f"当前值 {value_ns:.3f}{limit.unit} 低于推荐值 {limit.jedec_min}{limit.unit}"
        )

    return (RiskLevel.SAFE, "")
