"""
Módulo del Sistema de Alertas Tempranas (Early Warning System - EWS).
Detección preventiva de estrés financiero y alertas de vulnerabilidad crediticia.
Proyecto de Residencia Profesional: Marco Antonio Oroza Ortega - TESE (Informática).
"""

from typing import Dict, Any, List
import pandas as pd
import numpy as np


# Definición formal de los 4 Indicadores de Alerta Temprana (EWIs)
EWI_CATALOG = {
    "EWI_USO_CRITICO": {
        "codigo": "EWI_01_USO_CRITICO",
        "nombre": "Apalancamiento Alto",
        "descripcion": "Utilización de línea >= 85%, señal de saturación de crédito."
    },
    "EWI_FATIGA_MINIMOS": {
        "codigo": "EWI_02_FATIGA_MINIMOS",
        "nombre": "Dependencia de Pagos Mínimos",
        "descripcion": "2 o más pagos mínimos consecutivos, señal de estrés de liquidez."
    },
    "EWI_MORA_INCIPIENTE": {
        "codigo": "EWI_03_MORA_INCIPIENTE",
        "nombre": "Mora Temprana Acelerada",
        "descripcion": "Atraso incipiente (1 a 29 días) con tendencia creciente respecto al mes previo."
    },
    "EWI_SOBREGIRO_HISTORICO": {
        "codigo": "EWI_04_SOBREGIRO_HISTORICO",
        "nombre": "Vulnerabilidad Presupuestal",
        "descripcion": "Al menos 1 sobregiro reciente o antecedentes de reestructuración crediticia."
    }
}


class EarlyWarningSystem:
    """
    Motor del Sistema de Alertas Tempranas (EWS).
    Evalúa patrones de vulnerabilidad antes de que se materialice la cartera vencida.
    """

    def __init__(self, umbral_uso: float = 85.0, min_pagos_minimos: int = 2):
        self.umbral_uso = umbral_uso
        self.min_pagos_minimos = min_pagos_minimos

    def evaluate_portfolio(self, df_features: pd.DataFrame) -> pd.DataFrame:
        """
        Evalúa toda la cartera y calcula las banderas individuales, el total de alertas
        y el nivel de riesgo preventivo asignado.
        """
        df_out = df_features.copy()

        # 1. Bandera: Uso crítico de línea
        df_out["FLAG_EWI_USO"] = (df_out["PORC_USO_LINEA"] >= self.umbral_uso).astype(int)

        # 2. Bandera: Dependencia de pagos mínimos
        df_out["FLAG_EWI_MINIMOS"] = (df_out["PAGOS_MINIMOS_CONSECUTIVOS"] >= self.min_pagos_minimos).astype(int)

        # 3. Bandera: Mora incipiente creciente (< 30 días pero M1 > M2 o M1 > 0)
        df_out["FLAG_EWI_MORA_INCIPIENTE"] = (
            (df_out["DIAS_ATRASO_M1"] > 0) & 
            (df_out["DIAS_ATRASO_M1"] < 30) & 
            (df_out["DIAS_ATRASO_M1"] >= df_out["DIAS_ATRASO_M2"])
        ).astype(int)

        # 4. Bandera: Vulnerabilidad por sobregiros o reestructura previa
        df_out["FLAG_EWI_VULNERABILIDAD"] = (
            (df_out["NUM_SOBREGIROS_U6M"] >= 1) | 
            (df_out["FLAG_REESTRUCTURA_PREVIA"] == 1)
        ).astype(int)

        # Contador total de alertas activas (0 a 4)
        df_out["NUM_ALERTAS_EWI"] = (
            df_out["FLAG_EWI_USO"] + 
            df_out["FLAG_EWI_MINIMOS"] + 
            df_out["FLAG_EWI_MORA_INCIPIENTE"] + 
            df_out["FLAG_EWI_VULNERABILIDAD"]
        )

        # Asignación del Nivel de Riesgo Preventivo EWS
        conditions = [
            df_out["NUM_ALERTAS_EWI"] >= 3,
            df_out["NUM_ALERTAS_EWI"] == 2,
            df_out["NUM_ALERTAS_EWI"] == 1,
            df_out["NUM_ALERTAS_EWI"] == 0
        ]
        niveles = [
            "ROJO_CRITICO",
            "NARANJA_MODERADO",
            "AMARILLO_VIGILANCIA",
            "VERDE_NORMAL"
        ]
        df_out["NIVEL_RIESGO_EWI"] = np.select(conditions, niveles, default="VERDE_NORMAL")

        # Acción preventiva recomendada
        acciones = [
            "BLOQUEO_PREVENTIVO_Y_CONTACTO_RETENCION",
            "REDUCIR_LINEA_Y_RESTRINGIR_SOBREGIROS",
            "CONGELAR_OFERTAS_Y_RECORDATORIO_PREVENTIVO",
            "MONITOREO_ESTANDAR_SIN_RESTRICCION"
        ]
        df_out["ACCION_PREVENTIVA_EWI"] = np.select(conditions, acciones, default="MONITOREO_ESTANDAR_SIN_RESTRICCION")

        return df_out

    def generate_ews_summary(self, df_evaluated: pd.DataFrame) -> Dict[str, Any]:
        """Genera métricas consolidadas del Sistema de Alertas Tempranas."""
        total = len(df_evaluated)
        dist_niveles = df_evaluated["NIVEL_RIESGO_EWI"].value_counts().to_dict()
        
        return {
            "total_cuentas": total,
            "distribucion_niveles": dist_niveles,
            "ocurrencias_indicadores": {
                "uso_critico": int(df_evaluated["FLAG_EWI_USO"].sum()),
                "fatiga_minimos": int(df_evaluated["FLAG_EWI_MINIMOS"].sum()),
                "mora_incipiente": int(df_evaluated["FLAG_EWI_MORA_INCIPIENTE"].sum()),
                "vulnerabilidad_presupuestal": int(df_evaluated["FLAG_EWI_VULNERABILIDAD"].sum())
            },
            "porcentaje_en_riesgo_activo": round(
                ((df_evaluated["NUM_ALERTAS_EWI"] >= 2).sum() / max(1, total)) * 100, 2
            )
        }
