"""
Orquestador de Estrategias y Árbol de Prelación Jerárquica (Strategy Manager).
Emula el módulo Strategy Design de Experian PowerCurve.
"""

from typing import Optional
import pandas as pd
import numpy as np
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


class DecisionEngine:
    """
    Motor de Decisiones Comportamentales.
    Aplica las políticas de crédito en estricto orden de prelación:
    1. Knock-Out Severo (Prioridad 1)
    2. Contención Inmediata (Prioridad 2)
    3. Mitigación Preventiva (Prioridad 3)
    4. Expansión Proactiva (Prioridad 4)
    5. Política Residual / Mantenimiento (Prioridad 5)
    """

    def __init__(self, params: Optional[PolicyParameters] = None):
        self.params = params or PolicyParameters()

    def process_portfolio(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Ejecuta el pipeline de decisión sobre toda la cartera crediticia.
        Retorna el DataFrame enriquecido con la decisión, nuevo límite, estatus,
        código de razón y variación de exposición monetaria.
        """
        df_out = df_features.copy()
        n = len(df_out)

        # Máscaras de reglas evaluadas de forma aislada
        mask_r1 = evaluate_rule_1_knockout(df_out, self.params)
        mask_r2 = evaluate_rule_2_contencion(df_out, self.params)
        mask_r3 = evaluate_rule_3_mitigacion(df_out, self.params)
        mask_r4 = evaluate_rule_4_expansion(df_out, self.params)

        # Aplicación del Árbol de Prelación Jerárquica (Precedence Tree)
        # 1. Regla 1 tiene máxima prioridad
        applied_r1 = mask_r1

        # 2. Regla 2 se aplica si cumple R2 y NO fue interceptado por R1
        applied_r2 = mask_r2 & (~applied_r1)

        # 3. Regla 3 se aplica si cumple R3 y NO fue interceptado por R1 ni R2
        applied_r3 = mask_r3 & (~applied_r1) & (~applied_r2)

        # 4. Regla 4 se aplica si cumple R4 y NO fue interceptado por R1, R2 ni R3
        applied_r4 = mask_r4 & (~applied_r1) & (~applied_r2) & (~applied_r3)

        # 5. Residual: todo lo que no detonó ninguna de las 4 anteriores
        applied_r0 = (~applied_r1) & (~applied_r2) & (~applied_r3) & (~applied_r4)

        # Asignación de Identificador de Regla Disparada
        regla_disparada = np.select(
            [applied_r1, applied_r2, applied_r3, applied_r4, applied_r0],
            ["R1_KNOCKOUT", "R2_CONTENCION", "R3_MITIGACION", "R4_EXPANSION", "R0_MANTENIMIENTO"],
            default="R0_MANTENIMIENTO"
        )
        df_out["REGLA_DISPARADA"] = regla_disparada

        # Asignación de Nombre de Decisión
        df_out["DECISION_FINAL"] = np.select(
            [applied_r1, applied_r2, applied_r3, applied_r4, applied_r0],
            [
                DECISION_NAMES["R1_KNOCKOUT"],
                DECISION_NAMES["R2_CONTENCION"],
                DECISION_NAMES["R3_MITIGACION"],
                DECISION_NAMES["R4_EXPANSION"],
                DECISION_NAMES["R0_MANTENIMIENTO"]
            ],
            default=DECISION_NAMES["R0_MANTENIMIENTO"]
        )

        # Asignación del Estatus Operativo de la Tarjeta/Línea
        df_out["ESTATUS_RESULTANTE"] = np.select(
            [applied_r1, applied_r2, applied_r3, applied_r4, applied_r0],
            [
                ESTATUS_CUENTA["R1_KNOCKOUT"],
                ESTATUS_CUENTA["R2_CONTENCION"],
                ESTATUS_CUENTA["R3_MITIGACION"],
                ESTATUS_CUENTA["R4_EXPANSION"],
                ESTATUS_CUENTA["R0_MANTENIMIENTO"]
            ],
            default=ESTATUS_CUENTA["R0_MANTENIMIENTO"]
        )

        # Asignación de Códigos de Razón (Reason Codes para Explicabilidad)
        df_out["CODIGO_RAZON"] = np.select(
            [applied_r1, applied_r2, applied_r3, applied_r4, applied_r0],
            [
                REASON_CODES["R1_KNOCKOUT"],
                REASON_CODES["R2_CONTENCION"],
                REASON_CODES["R3_MITIGACION"],
                REASON_CODES["R4_EXPANSION"],
                REASON_CODES["R0_MANTENIMIENTO"]
            ],
            default=REASON_CODES["R0_MANTENIMIENTO"]
        )

        # Cálculo Financiero del Nuevo Límite de Crédito
        # R1: 0.0
        limite_r1 = 0.0
        # R2: Mantiene el límite actual (pero tarjeta suspendida temporalmente)
        limite_r2 = df_out["LIMITE_CREDITO_ACTUAL"]

        # R3: Reducción preventiva (estática o por matriz dinámica de score)
        if self.params.habilitar_matriz_dinamica:
            factor_red = np.where(df_out["SCORE_COMPORTAMENTAL"] < 520, 0.50, 0.65)
            limite_r3 = np.maximum(
                df_out["SALDO_ACTUAL"] * self.params.factor_proteccion_saldo,
                df_out["LIMITE_CREDITO_ACTUAL"] * factor_red
            )
        else:
            limite_r3 = np.maximum(
                df_out["SALDO_ACTUAL"] * self.params.factor_proteccion_saldo,
                df_out["LIMITE_CREDITO_ACTUAL"] * self.params.factor_reduccion_linea
            )

        # R4: Incremento de línea (estático o por matriz escalonada de score Prime)
        if self.params.habilitar_matriz_dinamica:
            factor_inc = np.select(
                [df_out["SCORE_COMPORTAMENTAL"] >= 800, df_out["SCORE_COMPORTAMENTAL"] >= 750],
                [1.35, 1.25],
                default=1.15
            )
            limite_r4 = np.round(df_out["LIMITE_CREDITO_ACTUAL"] * factor_inc, 2)
        else:
            limite_r4 = np.round(df_out["LIMITE_CREDITO_ACTUAL"] * self.params.factor_incremento_linea, 2)

        # R0: Límite original sin cambios
        limite_r0 = df_out["LIMITE_CREDITO_ACTUAL"]

        df_out["NUEVO_LIMITE_CREDITO"] = np.select(
            [applied_r1, applied_r2, applied_r3, applied_r4, applied_r0],
            [limite_r1, limite_r2, limite_r3, limite_r4, limite_r0],
            default=limite_r0
        )
        df_out["NUEVO_LIMITE_CREDITO"] = np.round(df_out["NUEVO_LIMITE_CREDITO"], 2)

        # Variación Neta de Exposición de Crédito (Delta Financiero)
        df_out["DELTA_EXPOSICION"] = np.round(
            df_out["NUEVO_LIMITE_CREDITO"] - df_out["LIMITE_CREDITO_ACTUAL"], 2
        )

        return df_out
