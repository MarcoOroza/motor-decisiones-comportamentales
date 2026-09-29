"""
Capa de Ingeniería de Variables Comportamentales (Feature Engineering).
Calcula indicadores de estrés crediticio, deltas de morosidad y ratios de apalancamiento.
"""

import pandas as pd
import numpy as np


def compute_behavioral_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Toma un DataFrame validado de cuentas y calcula las variables derivadas necesarias
    para la ejecución de las políticas del motor de decisiones.
    """
    df_feat = df.copy()

    # 1. Porcentaje de uso de línea (Ratio de Apalancamiento en %)
    # Protegemos contra división por cero
    limite_seguro = np.where(df_feat["LIMITE_CREDITO_ACTUAL"] <= 0, 1.0, df_feat["LIMITE_CREDITO_ACTUAL"])
    df_feat["PORC_USO_LINEA"] = np.round((df_feat["SALDO_ACTUAL"] / limite_seguro) * 100.0, 2)

    # 2. Saldo disponible real
    df_feat["SALDO_DISPONIBLE"] = np.maximum(0.0, df_feat["LIMITE_CREDITO_ACTUAL"] - df_feat["SALDO_ACTUAL"])

    # 3. Deltas de morosidad (Roll-forward y tendencia de deterioro)
    df_feat["DELTA_MORA_M1_M2"] = df_feat["DIAS_ATRASO_M1"] - df_feat["DIAS_ATRASO_M2"]
    df_feat["DELTA_MORA_M2_M3"] = df_feat["DIAS_ATRASO_M2"] - df_feat["DIAS_ATRASO_M3"]

    # 4. Indicador de deterioro activo (mora creciente en el último mes)
    df_feat["FLAG_DETERIORO_ACTIVO"] = (
        (df_feat["DIAS_ATRASO_M1"] > df_feat["DIAS_ATRASO_M2"]) & 
        (df_feat["DIAS_ATRASO_M1"] > 0)
    ).astype(int)

    # 5. Segmentación de Score Comportamental (Estándar FICO/PowerCurve)
    conditions = [
        df_feat["SCORE_COMPORTAMENTAL"] >= 720,
        (df_feat["SCORE_COMPORTAMENTAL"] >= 650) & (df_feat["SCORE_COMPORTAMENTAL"] < 720),
        (df_feat["SCORE_COMPORTAMENTAL"] >= 580) & (df_feat["SCORE_COMPORTAMENTAL"] < 650),
        df_feat["SCORE_COMPORTAMENTAL"] < 580
    ]
    choices = ["PRIME_EXCELENTE", "MEDIO_ESTABLE", "MEDIO_VULNERABLE", "SUBPRIME_ALTO_RIESGO"]
    df_feat["SEGMENTO_SCORE"] = np.select(conditions, choices, default="MEDIO_ESTABLE")

    # 6. Indicador de estrés por pagos mínimos recurrentes
    df_feat["FLAG_ESTRES_MINIMOS"] = (df_feat["PAGOS_MINIMOS_CONSECUTIVOS"] >= 3).astype(int)

    return df_feat
