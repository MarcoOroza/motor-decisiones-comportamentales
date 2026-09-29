"""
Batería de Pruebas Unitarias y de Regresión para el Motor de Decisiones.
Verifica cumplimiento estricto de la Sección 4 (Reglas de Negocio y Precedencia).
"""

import pytest
import pandas as pd
from src.schema.account_schema import validate_portfolio_df
from src.pipeline.feature_engineering import compute_behavioral_features
from src.engine.rules import PolicyParameters, REASON_CODES, DECISION_NAMES
from src.engine.strategy_manager import DecisionEngine
from src.engine.audit import generate_audit_summary


@pytest.fixture
def engine():
    return DecisionEngine(PolicyParameters())


def make_single_account_df(**kwargs):
    default_record = {
        "ID_CLIENTE": "CLI-10000001",
        "ID_CONTRATO": "ACC-5000000001",
        "LIMITE_CREDITO_ACTUAL": 50000.0,
        "SALDO_ACTUAL": 15000.0,
        "DIAS_ATRASO_M1": 0,
        "DIAS_ATRASO_M2": 0,
        "DIAS_ATRASO_M3": 0,
        "PAGOS_MINIMOS_CONSECUTIVOS": 0,
        "NUM_SOBREGIROS_U6M": 0,
        "SCORE_COMPORTAMENTAL": 680,
        "ANTIGUEDAD_CUENTA_MESES": 24,
        "FLAG_REESTRUCTURA_PREVIA": 0
    }
    default_record.update(kwargs)
    df = pd.DataFrame([default_record])
    df_clean, _ = validate_portfolio_df(df)
    return compute_behavioral_features(df_clean)


def test_rule_1_knockout_mora_90(engine):
    """Prueba Regla 1: Cliente con mora >= 90 días debe ser cancelado y enviado a cobranza."""
    df = make_single_account_df(DIAS_ATRASO_M1=90, SCORE_COMPORTAMENTAL=750)
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R1_KNOCKOUT"]
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 0.0
    assert result.iloc[0]["ESTATUS_RESULTANTE"] == "CANCELADA_POR_RIESGO"
    assert result.iloc[0]["CODIGO_RAZON"] == REASON_CODES["R1_KNOCKOUT"]
    assert result.iloc[0]["DELTA_EXPOSICION"] == -50000.0


def test_rule_1_knockout_reestructura_mora_30(engine):
    """Prueba Regla 1: Reestructura previa con atraso >= 30 días es Knock-out."""
    df = make_single_account_df(FLAG_REESTRUCTURA_PREVIA=1, DIAS_ATRASO_M1=30)
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R1_KNOCKOUT"]
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 0.0


def test_rule_2_contencion_roll_forward(engine):
    """Prueba Regla 2: Mora creciente M1 >= 30 y M1 > M2 suspende la tarjeta temporalmente."""
    df = make_single_account_df(DIAS_ATRASO_M1=35, DIAS_ATRASO_M2=15)
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R2_CONTENCION"]
    assert result.iloc[0]["ESTATUS_RESULTANTE"] == "SUSPENDIDA_TEMPORAL"
    assert result.iloc[0]["CODIGO_RAZON"] == REASON_CODES["R2_CONTENCION"]
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 50000.0


def test_rule_2_contencion_uso_critico_mora(engine):
    """Prueba Regla 2: Uso >= 95% y mora M1 >= 15 días congela la cuenta."""
    df = make_single_account_df(
        LIMITE_CREDITO_ACTUAL=20000.0,
        SALDO_ACTUAL=19200.0, # 96% de uso
        DIAS_ATRASO_M1=16,
        DIAS_ATRASO_M2=0
    )
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R2_CONTENCION"]
    assert result.iloc[0]["ESTATUS_RESULTANTE"] == "SUSPENDIDA_TEMPORAL"


def test_rule_3_mitigacion_score_bajo_alto_uso(engine):
    """Prueba Regla 3: Score < 580 y uso >= 80% reduce la línea al 60% protegiendo saldo."""
    df = make_single_account_df(
        LIMITE_CREDITO_ACTUAL=50000.0,
        SALDO_ACTUAL=41000.0, # 82% uso
        SCORE_COMPORTAMENTAL=560,
        DIAS_ATRASO_M1=0
    )
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R3_MITIGACION"]
    assert result.iloc[0]["ESTATUS_RESULTANTE"] == "ACTIVA_REDUCIDA"
    assert result.iloc[0]["CODIGO_RAZON"] == REASON_CODES["R3_MITIGACION"]
    # 50,000 * 0.60 = 30,000, pero saldo * 1.05 = 41,000 * 1.05 = 43,050
    # Por regla, nuevo límite = max(43,050, 30,000) = 43,050 para evitar sobregiro artificial
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 43050.0
    assert result.iloc[0]["DELTA_EXPOSICION"] < 0


def test_rule_3_mitigacion_minimos_consecutivos(engine):
    """Prueba Regla 3: Pagos mínimos >= 4 y Score < 620 detona reducción preventiva."""
    df = make_single_account_df(
        LIMITE_CREDITO_ACTUAL=30000.0,
        SALDO_ACTUAL=12000.0,
        PAGOS_MINIMOS_CONSECUTIVOS=5,
        SCORE_COMPORTAMENTAL=610,
        DIAS_ATRASO_M1=0
    )
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R3_MITIGACION"]
    # 30,000 * 0.60 = 18,000; saldo * 1.05 = 12,600 -> toma 18,000
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 18000.0


def test_rule_4_expansion_prime(engine):
    """Prueba Regla 4: Cliente Prime excelente recibe incremento del 25%."""
    df = make_single_account_df(
        LIMITE_CREDITO_ACTUAL=40000.0,
        SALDO_ACTUAL=20000.0, # 50% uso
        SCORE_COMPORTAMENTAL=760,
        DIAS_ATRASO_M1=0,
        DIAS_ATRASO_M2=0,
        DIAS_ATRASO_M3=0,
        ANTIGUEDAD_CUENTA_MESES=18,
        NUM_SOBREGIROS_U6M=0,
        FLAG_REESTRUCTURA_PREVIA=0
    )
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R4_EXPANSION"]
    assert result.iloc[0]["ESTATUS_RESULTANTE"] == "ACTIVA_PREMIUM"
    assert result.iloc[0]["CODIGO_RAZON"] == REASON_CODES["R4_EXPANSION"]
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 50000.0 # 40,000 * 1.25
    assert result.iloc[0]["DELTA_EXPOSICION"] == 10000.0


def test_rule_0_mantenimiento_regular(engine):
    """Prueba Residual: Cliente estándar conserva sus condiciones."""
    df = make_single_account_df(
        LIMITE_CREDITO_ACTUAL=30000.0,
        SALDO_ACTUAL=5000.0, # 16% uso (fuera de rango de expansión 40-75%)
        SCORE_COMPORTAMENTAL=680, # Fuera de prime (>= 720) y fuera de fatiga (< 580)
        DIAS_ATRASO_M1=0
    )
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R0_MANTENIMIENTO"]
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 30000.0
    assert result.iloc[0]["DELTA_EXPOSICION"] == 0.0


def test_precedence_hierarchy_protection(engine):
    """
    CRÍTICO: Si un cliente tiene score Prime (800) pero cayó en mora de 95 días,
    la Regla 1 (Knock-out) DEBE prevalecer sobre la Regla 4 (Expansión).
    Jamás debe otorgarse un incremento a un cliente en default.
    """
    df = make_single_account_df(
        SCORE_COMPORTAMENTAL=820,
        LIMITE_CREDITO_ACTUAL=60000.0,
        SALDO_ACTUAL=30000.0, # 50% uso
        DIAS_ATRASO_M1=95,    # Mora severa!
        DIAS_ATRASO_M2=0,
        DIAS_ATRASO_M3=0,
        ANTIGUEDAD_CUENTA_MESES=36,
        NUM_SOBREGIROS_U6M=0
    )
    result = engine.process_portfolio(df)
    
    assert result.iloc[0]["DECISION_FINAL"] == DECISION_NAMES["R1_KNOCKOUT"]
    assert result.iloc[0]["NUEVO_LIMITE_CREDITO"] == 0.0
    assert result.iloc[0]["CODIGO_RAZON"] == REASON_CODES["R1_KNOCKOUT"]


def test_audit_summary_generation(engine):
    """Prueba que el resumen de auditoría calcule con precisión los deltas financieros."""
    df1 = make_single_account_df(SCORE_COMPORTAMENTAL=760, LIMITE_CREDITO_ACTUAL=40000.0, SALDO_ACTUAL=20000.0) # +10,000
    df2 = make_single_account_df(DIAS_ATRASO_M1=95, LIMITE_CREDITO_ACTUAL=50000.0, SALDO_ACTUAL=50000.0)         # -50,000
    df_combined = pd.concat([df1, df2], ignore_index=True)
    
    decisions = engine.process_portfolio(df_combined)
    audit = generate_audit_summary(decisions)
    
    assert audit["total_cuentas_procesadas"] == 2
    assert audit["metricas_financieras"]["limite_vigente_total_mxn"] == 90000.0
    assert audit["metricas_financieras"]["nuevo_limite_total_mxn"] == 50000.0
    assert audit["metricas_financieras"]["delta_exposicion_neta_mxn"] == -40000.0
