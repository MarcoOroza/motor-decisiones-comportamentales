"""Módulo del motor de decisiones y auditoría."""
from src.engine.rules import (
    PolicyParameters,
    REASON_CODES,
    DECISION_NAMES,
    ESTATUS_CUENTA,
    evaluate_rule_1_knockout,
    evaluate_rule_2_contencion,
    evaluate_rule_3_mitigacion,
    evaluate_rule_4_expansion,
)
from src.engine.strategy_manager import DecisionEngine
from src.engine.audit import generate_audit_summary
from src.engine.champion_challenger import ChampionChallengerSimulator

__all__ = [
    "PolicyParameters",
    "REASON_CODES",
    "DECISION_NAMES",
    "ESTATUS_CUENTA",
    "DecisionEngine",
    "ChampionChallengerSimulator",
    "generate_audit_summary",
    "evaluate_rule_1_knockout",
    "evaluate_rule_2_contencion",
    "evaluate_rule_3_mitigacion",
    "evaluate_rule_4_expansion",
]
