"""
Módulo de Auditoría y Trazabilidad de Decisiones (Audit Trail & Governance).
Genera registros inmutables requeridos por normativas bancarias (CNBV / Basilea).
"""

from datetime import datetime
import uuid
from typing import Dict, Any
import pandas as pd


def generate_audit_summary(df_decisions: pd.DataFrame, strategy_name: str = "PowerCurve_Behavioral_v1") -> Dict[str, Any]:
    """
    Genera un informe consolidado de auditoría para comités de riesgo y control normativo.
    """
    total_cuentas = len(df_decisions)
    distribucion_decisiones = df_decisions["DECISION_FINAL"].value_counts().to_dict()
    distribucion_reglas = df_decisions["REGLA_DISPARADA"].value_counts().to_dict()
    distribucion_estatus = df_decisions["ESTATUS_RESULTANTE"].value_counts().to_dict()
    
    limite_actual_total = float(df_decisions["LIMITE_CREDITO_ACTUAL"].sum())
    nuevo_limite_total = float(df_decisions["NUEVO_LIMITE_CREDITO"].sum())
    delta_exposicion_total = float(df_decisions["DELTA_EXPOSICION"].sum())
    saldo_total_expuesto = float(df_decisions["SALDO_ACTUAL"].sum())

    resumen = {
        "execution_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "strategy_name": strategy_name,
        "total_cuentas_procesadas": total_cuentas,
        "distribucion_decisiones": distribucion_decisiones,
        "distribucion_reglas": distribucion_reglas,
        "distribucion_estatus": distribucion_estatus,
        "metricas_financieras": {
            "limite_vigente_total_mxn": round(limite_actual_total, 2),
            "nuevo_limite_total_mxn": round(nuevo_limite_total, 2),
            "delta_exposicion_neta_mxn": round(delta_exposicion_total, 2),
            "saldo_cartera_evaluada_mxn": round(saldo_total_expuesto, 2),
            "porcentaje_variacion_linea": round((delta_exposicion_total / max(1.0, limite_actual_total)) * 100, 2)
        }
    }
    return resumen
