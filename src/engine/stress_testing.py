"""
Módulo de Pruebas de Estrés Masivo y Análisis de Sensibilidad Macroeconómica (Stress Testing).
Evaluación de rendimiento computacional (hasta 100,000 contratos) y resistencia sistémica bajo IFRS 9 / Basilea.
Proyecto de Residencia Profesional: Marco Antonio Oroza Ortega - TESE (División de Informática).
"""

import time
import tracemalloc
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd

from src.data_generator import generate_synthetic_portfolio
from src.schema.account_schema import validate_portfolio_df
from src.pipeline.feature_engineering import compute_behavioral_features
from src.engine.rules import PolicyParameters
from src.engine.strategy_manager import DecisionEngine
from src.engine.early_warning import EarlyWarningSystem
from src.engine.audit import generate_audit_summary


# Definición de Escenarios de Choque Macroeconómico
MACRO_SCENARIOS = {
    "baseline": {
        "nombre": "Línea Base (Condiciones Normales)",
        "descripcion": "Cartera operando en régimen normal de estabilidad macroeconómica."
    },
    "recesion": {
        "nombre": "Escenario Adverso (Recesión Económica)",
        "descripcion": "Contracción económica, aumento de inflación, mora +15%, uso +15% y caída de Score FICO -35 pts."
    },
    "crisis": {
        "nombre": "Escenario Severamente Adverso (Crisis Sistémica)",
        "descripcion": "Shock severo de desempleo, corrida de líneas +25%, mora +35% y desplome de Score FICO -70 pts."
    }
}


def apply_macroeconomic_shock(
    df: pd.DataFrame,
    scenario: str = "baseline",
    random_seed: int = 42
) -> pd.DataFrame:
    """
    Aplica perturbaciones macroeconómicas controladas sobre una cartera de contratos.
    Modela el impacto de ciclos económicos adversos según directrices de Basilea e IFRS 9.
    """
    np.random.seed(random_seed)
    df_shock = df.copy()

    if scenario == "baseline":
        return df_shock

    elif scenario == "recesion":
        # 1. Caída moderada de Score FICO
        df_shock["SCORE_COMPORTAMENTAL"] = np.clip(
            df_shock["SCORE_COMPORTAMENTAL"] - 35, 300, 850
        ).astype(int)

        # 2. Incremento de uso de línea (fatiga de liquidez)
        df_shock["SALDO_ACTUAL"] = np.clip(
            df_shock["SALDO_ACTUAL"] * 1.15,
            0,
            df_shock["LIMITE_CREDITO_ACTUAL"] * 1.25
        ).round(2)

        # 3. Choque de morosidad incipiente y persistente
        mora_shock = np.random.choice([0, 5, 15, 30], len(df_shock), p=[0.40, 0.30, 0.20, 0.10])
        df_shock["DIAS_ATRASO_M1"] = np.clip(df_shock["DIAS_ATRASO_M1"] + mora_shock, 0, 180).astype(int)

        # 4. Incremento de dependencia de pagos mínimos
        minimos_shock = np.random.choice([0, 1, 2], len(df_shock), p=[0.50, 0.30, 0.20])
        df_shock["PAGOS_MINIMOS_CONSECUTIVOS"] = np.clip(
            df_shock["PAGOS_MINIMOS_CONSECUTIVOS"] + minimos_shock, 0, 12
        ).astype(int)

    elif scenario == "crisis":
        # 1. Desplome severo de solvencia FICO
        df_shock["SCORE_COMPORTAMENTAL"] = np.clip(
            df_shock["SCORE_COMPORTAMENTAL"] - 70, 300, 850
        ).astype(int)

        # 2. Corrida de líneas de crédito (retiro masivo de liquidez disponible)
        df_shock["SALDO_ACTUAL"] = np.clip(
            df_shock["SALDO_ACTUAL"] * 1.25,
            0,
            df_shock["LIMITE_CREDITO_ACTUAL"] * 1.35
        ).round(2)

        # 3. Transición acelerada a mora severa (roll forward masivo)
        mora_crisis = np.random.choice([0, 15, 35, 65], len(df_shock), p=[0.20, 0.30, 0.30, 0.20])
        df_shock["DIAS_ATRASO_M1"] = np.clip(df_shock["DIAS_ATRASO_M1"] + mora_crisis, 0, 240).astype(int)

        # 4. Asfixia de pagos mínimos reiterados
        minimos_crisis = np.random.choice([1, 2, 3], len(df_shock), p=[0.30, 0.40, 0.30])
        df_shock["PAGOS_MINIMOS_CONSECUTIVOS"] = np.clip(
            df_shock["PAGOS_MINIMOS_CONSECUTIVOS"] + minimos_crisis, 0, 12
        ).astype(int)

        # 5. Sobregiros presupuestales
        sobregiros_crisis = np.random.choice([0, 1, 2], len(df_shock), p=[0.40, 0.40, 0.20])
        df_shock["NUM_SOBREGIROS_U6M"] = np.clip(
            df_shock["NUM_SOBREGIROS_U6M"] + sobregiros_crisis, 0, 6
        ).astype(int)

    return df_shock


def run_scalability_benchmark(
    batch_sizes: Optional[List[int]] = None,
    random_seed: int = 42
) -> List[Dict[str, Any]]:
    """
    Ejecuta pruebas de carga computacional en memoria sobre volúmenes masivos de contratos.
    Mide tiempo de ejecución, latencia unitaria, throughput y consumo de memoria RAM.
    """
    if batch_sizes is None:
        batch_sizes = [2500, 10000, 25000, 50000, 100000]

    policy = PolicyParameters(habilitar_matriz_dinamica=True)
    engine = DecisionEngine(policy)
    ews = EarlyWarningSystem()

    benchmark_records = []

    for n in batch_sizes:
        df_raw = generate_synthetic_portfolio(n, random_seed=random_seed)

        tracemalloc.start()
        t_global_start = time.perf_counter()

        # Fase 1: Validación de Calidad de Datos
        t0 = time.perf_counter()
        df_clean, _ = validate_portfolio_df(df_raw)
        t_val = time.perf_counter() - t0

        # Fase 2: Ingeniería de Variables Vectoriales
        t0 = time.perf_counter()
        df_feat = compute_behavioral_features(df_clean)
        t_feat = time.perf_counter() - t0

        # Fase 3: Árbol Jerárquico de Decisiones
        t0 = time.perf_counter()
        df_dec = engine.process_portfolio(df_feat)
        t_dec = time.perf_counter() - t0

        # Fase 4: Sistema de Alertas Tempranas (EWS)
        t0 = time.perf_counter()
        df_eval = ews.evaluate_portfolio(df_dec)
        t_ews = time.perf_counter() - t0

        # Fase 5: Auditoría y Resumen
        t0 = time.perf_counter()
        audit = generate_audit_summary(df_eval)
        t_aud = time.perf_counter() - t0

        t_global_total = time.perf_counter() - t_global_start
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        throughput = n / max(1e-6, t_global_total)
        latency_us = (t_global_total / n) * 1e6
        peak_mb = peak_bytes / (1024 * 1024)

        benchmark_records.append({
            "volumen_cuentas": n,
            "tiempo_total_seg": round(t_global_total, 4),
            "throughput_ops_seg": round(throughput, 1),
            "latencia_unitaria_us": round(latency_us, 2),
            "memoria_pico_mb": round(peak_mb, 2),
            "desglose_etapas": {
                "validacion_schema_seg": round(t_val, 4),
                "feature_engineering_seg": round(t_feat, 4),
                "motor_decisiones_seg": round(t_dec, 4),
                "early_warning_seg": round(t_ews, 4),
                "auditoria_resumen_seg": round(t_aud, 4)
            }
        })

    return benchmark_records


def run_stress_scenario_comparison(
    df_base: pd.DataFrame,
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Evalúa la cartera bajo los 3 escenarios macroeconómicos (Línea Base, Recesión, Crisis).
    Demuestra la resistencia del motor y la contracción preventiva de exposición.
    """
    policy = PolicyParameters(habilitar_matriz_dinamica=True)
    engine = DecisionEngine(policy)
    ews = EarlyWarningSystem()

    scenarios_summary = {}

    for sc_key in ["baseline", "recesion", "crisis"]:
        df_shocked = apply_macroeconomic_shock(df_base, scenario=sc_key, random_seed=random_seed)
        df_clean, _ = validate_portfolio_df(df_shocked)
        df_feat = compute_behavioral_features(df_clean)
        df_dec = engine.process_portfolio(df_feat)
        df_eval = ews.evaluate_portfolio(df_dec)
        audit = generate_audit_summary(df_eval)
        ews_s = ews.generate_ews_summary(df_eval)

        scenarios_summary[sc_key] = {
            "info": MACRO_SCENARIOS[sc_key],
            "total_cuentas": len(df_eval),
            "metricas_financieras": audit["metricas_financieras"],
            "distribucion_decisiones": audit["distribucion_decisiones"],
            "distribucion_ews": ews_s["distribucion_niveles"],
            "porcentaje_riesgo_activo": ews_s["porcentaje_en_riesgo_activo"]
        }

    return scenarios_summary
