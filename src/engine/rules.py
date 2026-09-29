"""
Definición Formal de Reglas de Negocio del Motor de Decisiones Comportamentales.
Basado estrictamente en la Sección 4 del documento de especificación técnica.
"""

from dataclasses import dataclass
from typing import Dict, Any
import pandas as pd
import numpy as np


@dataclass
class PolicyParameters:
    """Parámetros configurables de la política de riesgo (Strategy Management)."""
    # Regla 1: Knock-Out Severo
    dias_mora_default: int = 90
    dias_mora_reestructura: int = 30
    
    # Regla 2: Contención Inmediata
    dias_mora_contencion: int = 30
    uso_linea_critico: float = 95.0
    dias_mora_sobregiro: int = 15
    
    # Regla 3: Mitigación Preventiva
    score_subprime: int = 580
    uso_linea_fatiga: float = 80.0
    minimos_consecutivos_alerta: int = 4
    score_minimos: int = 620
    factor_reduccion_linea: float = 0.60
    factor_proteccion_saldo: float = 1.05
    
    # Regla 4: Expansión Proactiva
    score_prime: int = 720
    uso_min_expansion: float = 40.0
    uso_max_expansion: float = 75.0
    antiguedad_min_meses: int = 12
    factor_incremento_linea: float = 1.25


# Códigos de Razón y Explicabilidad
REASON_CODES = {
    "R1_KNOCKOUT": "RC_DEFAULT_SEVERO_IFRS9",
    "R2_CONTENCION": "RC_DETERIORO_MORA_ROLLFORWARD_CRITICO",
    "R3_MITIGACION": "RC_ESTRES_FINANCIERO_PAGOS_MINIMOS_PERSISTENTES",
    "R4_EXPANSION": "RC_CLIENTE_PRIME_EXCELENTE_HISTORIAL",
    "R0_MANTENIMIENTO": "RC_PERFIL_DENTRO_DE_TOLERANCIA_ESTANDAR"
}

DECISION_NAMES = {
    "R1_KNOCKOUT": "CANCELAR_LINEA_Y_ENVIO_COBRANZA",
    "R2_CONTENCION": "BLOQUEO_TEMPORAL_LINEA",
    "R3_MITIGACION": "REDUCIR_LINEA_PREVENTIVA",
    "R4_EXPANSION": "INCREMENTAR_LINEA_PROACTIVO",
    "R0_MANTENIMIENTO": "MANTENER_CONDICIONES_ACTUALES"
}

ESTATUS_CUENTA = {
    "R1_KNOCKOUT": "CANCELADA_POR_RIESGO",
    "R2_CONTENCION": "SUSPENDIDA_TEMPORAL",
    "R3_MITIGACION": "ACTIVA_REDUCIDA",
    "R4_EXPANSION": "ACTIVA_PREMIUM",
    "R0_MANTENIMIENTO": "ACTIVA_REGULAR"
}


def evaluate_rule_1_knockout(df: pd.DataFrame, params: PolicyParameters) -> pd.Series:
    """
    Regla 1: Política Knock-Out de Riesgo Severo (IFRS 9 / Basilea)
    SI (DIAS_ATRASO_M1 >= 90) OR (FLAG_REESTRUCTURA_PREVIA == 1 AND DIAS_ATRASO_M1 >= 30)
    """
    cond1 = df["DIAS_ATRASO_M1"] >= params.dias_mora_default
    cond2 = (df["FLAG_REESTRUCTURA_PREVIA"] == 1) & (df["DIAS_ATRASO_M1"] >= params.dias_mora_reestructura)
    return cond1 | cond2


def evaluate_rule_2_contencion(df: pd.DataFrame, params: PolicyParameters) -> pd.Series:
    """
    Regla 2: Política de Contención Inmediata por Deterioro Acelerado
    SI (DIAS_ATRASO_M1 >= 30 AND DIAS_ATRASO_M1 > DIAS_ATRASO_M2) OR (PORC_USO_LINEA >= 95% AND DIAS_ATRASO_M1 >= 15)
    """
    cond_deterioro = (df["DIAS_ATRASO_M1"] >= params.dias_mora_contencion) & (df["DIAS_ATRASO_M1"] > df["DIAS_ATRASO_M2"])
    cond_uso_mora = (df["PORC_USO_LINEA"] >= params.uso_linea_critico) & (df["DIAS_ATRASO_M1"] >= params.dias_mora_sobregiro)
    return cond_deterioro | cond_uso_mora


def evaluate_rule_3_mitigacion(df: pd.DataFrame, params: PolicyParameters) -> pd.Series:
    """
    Regla 3: Política de Mitigación Preventiva de Exposición (Reducción de Línea)
    SI (SCORE < 580 AND PORC_USO_LINEA >= 80%) OR (PAGOS_MINIMOS >= 4 AND SCORE < 620)
    """
    cond_score_uso = (df["SCORE_COMPORTAMENTAL"] < params.score_subprime) & (df["PORC_USO_LINEA"] >= params.uso_linea_fatiga)
    cond_minimos_score = (df["PAGOS_MINIMOS_CONSECUTIVOS"] >= params.minimos_consecutivos_alerta) & (df["SCORE_COMPORTAMENTAL"] < params.score_minimos)
    return cond_score_uso | cond_minimos_score


def evaluate_rule_4_expansion(df: pd.DataFrame, params: PolicyParameters) -> pd.Series:
    """
    Regla 4: Política de Crecimiento Proactivo de Cartera (Incremento de Línea)
    SI SCORE >= 720 AND M1=0 AND M2=0 AND M3=0 AND 40% <= USO <= 75% AND ANTIGUEDAD >= 12 AND SOBREGIROS=0 AND REESTRUCTURA=0
    """
    cond_score = df["SCORE_COMPORTAMENTAL"] >= params.score_prime
    cond_cero_mora = (df["DIAS_ATRASO_M1"] == 0) & (df["DIAS_ATRASO_M2"] == 0) & (df["DIAS_ATRASO_M3"] == 0)
    cond_uso_saludable = (df["PORC_USO_LINEA"] >= params.uso_min_expansion) & (df["PORC_USO_LINEA"] <= params.uso_max_expansion)
    cond_antiguedad = df["ANTIGUEDAD_CUENTA_MESES"] >= params.antiguedad_min_meses
    cond_sin_sobregiros = df["NUM_SOBREGIROS_U6M"] == 0
    cond_sin_reestructura = df["FLAG_REESTRUCTURA_PREVIA"] == 0
    
    return cond_score & cond_cero_mora & cond_uso_saludable & cond_antiguedad & cond_sin_sobregiros & cond_sin_reestructura
