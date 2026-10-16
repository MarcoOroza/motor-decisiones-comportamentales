"""
Módulo de Simulación Champion / Challenger (A/B Testing de Estrategias de Riesgo).
Emula las pruebas de estrés y comparación de políticas en Experian PowerCurve.
"""

from typing import Dict, Any, Tuple
import pandas as pd
import numpy as np

from src.engine.rules import PolicyParameters
from src.engine.strategy_manager import DecisionEngine


class ChampionChallengerSimulator:
    """
    Orquestador de pruebas comparativas Champion vs Challenger.
    Permite evaluar el impacto de una política retadora (Challenger) frente a la
    política base actualmente vigente (Champion).
    """

    def __init__(
        self,
        champion_params: PolicyParameters,
        challenger_params: PolicyParameters,
        split_ratio: float = 0.80,
        random_seed: int = 42
    ):
        self.champion_engine = DecisionEngine(champion_params)
        self.challenger_engine = DecisionEngine(challenger_params)
        self.split_ratio = split_ratio
        self.random_seed = random_seed

    def simulate_split(self, df_features: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Divide la cartera según split_ratio (ej. 80% Champion, 20% Challenger)
        y ejecuta cada subconjunto con su respectivo motor de decisión.
        """
        np.random.seed(self.random_seed)
        df_eval = df_features.copy()

        # Asignación aleatoria determinística de grupo (A/B)
        random_probs = np.random.uniform(0.0, 1.0, len(df_eval))
        df_eval["ESTRATEGIA_ASIGNADA"] = np.where(random_probs < self.split_ratio, "CHAMPION", "CHALLENGER")

        df_champ_input = df_eval[df_eval["ESTRATEGIA_ASIGNADA"] == "CHAMPION"]
        df_chall_input = df_eval[df_eval["ESTRATEGIA_ASIGNADA"] == "CHALLENGER"]

        df_champ_res = self.champion_engine.process_portfolio(df_champ_input)
        df_chall_res = self.challenger_engine.process_portfolio(df_chall_input)

        df_final = pd.concat([df_champ_res, df_chall_res], ignore_index=True)

        resumen = self._build_comparative_kpis(df_champ_res, df_chall_res)
        return df_final, resumen

    def simulate_parallel_comparison(self, df_features: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Ejecuta el 100% de la cartera bajo ambas estrategias de forma paralela (What-If analysis)
        para medir exactamente qué cuentas cambiarían de decisión si se reemplazara el Champion.
        """
        df_champ = self.champion_engine.process_portfolio(df_features)
        df_chall = self.challenger_engine.process_portfolio(df_features)

        df_comp = df_features.copy()
        df_comp["DECISION_CHAMPION"] = df_champ["DECISION_FINAL"]
        df_comp["DECISION_CHALLENGER"] = df_chall["DECISION_FINAL"]
        df_comp["NUEVO_LIMITE_CHAMPION"] = df_champ["NUEVO_LIMITE_CREDITO"]
        df_comp["NUEVO_LIMITE_CHALLENGER"] = df_chall["NUEVO_LIMITE_CREDITO"]
        df_comp["DELTA_EXP_CHAMPION"] = df_champ["DELTA_EXPOSICION"]
        df_comp["DELTA_EXP_CHALLENGER"] = df_chall["DELTA_EXPOSICION"]
        df_comp["CAMBIO_DE_DECISION"] = df_comp["DECISION_CHAMPION"] != df_comp["DECISION_CHALLENGER"]

        resumen = self._build_comparative_kpis(df_champ, df_chall)
        return df_comp, resumen

    def _build_comparative_kpis(self, df_champ: pd.DataFrame, df_chall: pd.DataFrame) -> Dict[str, Any]:
        """Calcula métricas clave de desempeño comparativo."""
        n_champ = len(df_champ)
        n_chall = len(df_chall)

        def get_rate(df, decision_name):
            if len(df) == 0: return 0.0
            return round((df["DECISION_FINAL"] == decision_name).sum() / len(df) * 100, 2)

        return {
            "muestras": {
                "cuentas_champion": n_champ,
                "cuentas_challenger": n_chall
            },
            "tasas_champion": {
                "tasa_aumento_pct": get_rate(df_champ, "INCREMENTAR_LINEA_PROACTIVO"),
                "tasa_mantenimiento_pct": get_rate(df_champ, "MANTENER_CONDICIONES_ACTUALES"),
                "tasa_reduccion_pct": get_rate(df_champ, "REDUCIR_LINEA_PREVENTIVA"),
                "tasa_bloqueo_pct": get_rate(df_champ, "BLOQUEO_TEMPORAL_LINEA"),
                "tasa_cancelacion_pct": get_rate(df_champ, "CANCELAR_LINEA_Y_ENVIO_COBRANZA"),
                "delta_exposicion_mxn": round(float(df_champ["DELTA_EXPOSICION"].sum()), 2)
            },
            "tasas_challenger": {
                "tasa_aumento_pct": get_rate(df_chall, "INCREMENTAR_LINEA_PROACTIVO"),
                "tasa_mantenimiento_pct": get_rate(df_chall, "MANTENER_CONDICIONES_ACTUALES"),
                "tasa_reduccion_pct": get_rate(df_chall, "REDUCIR_LINEA_PREVENTIVA"),
                "tasa_bloqueo_pct": get_rate(df_chall, "BLOQUEO_TEMPORAL_LINEA"),
                "tasa_cancelacion_pct": get_rate(df_chall, "CANCELAR_LINEA_Y_ENVIO_COBRANZA"),
                "delta_exposicion_mxn": round(float(df_chall["DELTA_EXPOSICION"].sum()), 2)
            }
        }
