"""
Generador de Cartera Crediticia Sintética Realista.
Permite simular carteras bancarias de tarjetas de crédito con perfiles heterogéneos de riesgo.
"""

import os
from typing import Optional
import numpy as np
import pandas as pd


def generate_synthetic_portfolio(n_records: int = 2500, random_seed: int = 42) -> pd.DataFrame:
    """
    Genera un conjunto sintético balanceado de cuentas crediticias representativas
    de los diferentes segmentos de comportamiento en banca de consumo.
    """
    np.random.seed(random_seed)
    
    # Proporciones poblacionales típicas de cartera en banca minorista
    # 45% Regulares/Estables, 25% Prime elegibles a aumento, 15% Fatiga, 10% Deterioro, 5% Default
    n_prime = int(n_records * 0.25)
    n_fatiga = int(n_records * 0.15)
    n_deterioro = int(n_records * 0.10)
    n_default = int(n_records * 0.05)
    n_regular = n_records - (n_prime + n_fatiga + n_deterioro + n_default)

    records = []

    def make_account(idx, score, limite, saldo, m1, m2, m3, minimos, sobregiros, antiguedad, reestructura):
        return {
            "ID_CLIENTE": f"CLI-{idx + 10000000:08d}",
            "ID_CONTRATO": f"ACC-{idx + 5000000000:010d}",
            "LIMITE_CREDITO_ACTUAL": float(limite),
            "SALDO_ACTUAL": float(min(saldo, limite * 1.2)), # límite con posible sobregiro
            "DIAS_ATRASO_M1": int(m1),
            "DIAS_ATRASO_M2": int(m2),
            "DIAS_ATRASO_M3": int(m3),
            "PAGOS_MINIMOS_CONSECUTIVOS": int(minimos),
            "NUM_SOBREGIROS_U6M": int(sobregiros),
            "SCORE_COMPORTAMENTAL": int(score),
            "ANTIGUEDAD_CUENTA_MESES": int(antiguedad),
            "FLAG_REESTRUCTURA_PREVIA": int(reestructura),
        }

    curr_id = 1

    # 1. Segmento Prime (Elegibles para incremento R4)
    for _ in range(n_prime):
        limite = np.random.choice([15000, 25000, 35000, 50000, 80000, 120000])
        uso_pct = np.random.uniform(0.42, 0.72)
        saldo = round(limite * uso_pct, 2)
        score = np.random.randint(725, 835)
        antiguedad = np.random.randint(14, 84)
        records.append(make_account(
            curr_id, score, limite, saldo,
            m1=0, m2=0, m3=0,
            minimos=np.random.choice([0, 1]),
            sobregiros=0,
            antiguedad=antiguedad,
            reestructura=0
        ))
        curr_id += 1

    # 2. Segmento Regular / Estable (Mantenimiento R0)
    for _ in range(n_regular):
        limite = np.random.choice([8000, 12000, 20000, 30000, 45000])
        uso_pct = np.random.uniform(0.10, 0.78)
        saldo = round(limite * uso_pct, 2)
        score = np.random.randint(625, 715)
        m1 = np.random.choice([0, 0, 0, 5, 10])
        m2 = np.random.choice([0, 0, 5])
        m3 = 0
        minimos = np.random.choice([0, 1, 2])
        sobregiros = np.random.choice([0, 0, 1])
        antiguedad = np.random.randint(6, 60)
        records.append(make_account(
            curr_id, score, limite, saldo,
            m1=m1, m2=m2, m3=m3,
            minimos=minimos,
            sobregiros=sobregiros,
            antiguedad=antiguedad,
            reestructura=0
        ))
        curr_id += 1

    # 3. Segmento Fatiga Financiera (Reducción preventiva R3)
    for _ in range(n_fatiga):
        limite = np.random.choice([15000, 25000, 40000, 60000])
        # Dos variantes de la regla:
        # Variante A: Score < 580 y uso >= 80%
        # Variante B: Pagos mínimos >= 4 y Score < 620
        variante = np.random.choice(["A", "B"])
        if variante == "A":
            score = np.random.randint(480, 575)
            uso_pct = np.random.uniform(0.82, 0.94)
            minimos = np.random.randint(1, 4)
        else:
            score = np.random.randint(550, 615)
            uso_pct = np.random.uniform(0.60, 0.92)
            minimos = np.random.randint(4, 9)

        saldo = round(limite * uso_pct, 2)
        m1 = np.random.choice([0, 5, 10, 20])
        m2 = np.random.choice([0, 10])
        m3 = 0
        antiguedad = np.random.randint(10, 50)
        records.append(make_account(
            curr_id, score, limite, saldo,
            m1=m1, m2=m2, m3=m3,
            minimos=minimos,
            sobregiros=np.random.choice([0, 1, 2]),
            antiguedad=antiguedad,
            reestructura=0
        ))
        curr_id += 1

    # 4. Segmento Deterioro Acelerado (Bloqueo temporal R2)
    for _ in range(n_deterioro):
        limite = np.random.choice([10000, 20000, 35000, 50000])
        variante = np.random.choice(["roll_forward", "critico_uso"])
        if variante == "roll_forward":
            # M1 >= 30 y M1 > M2
            m2 = np.random.randint(5, 25)
            m1 = m2 + np.random.randint(10, 35) # e.g. M1=45, M2=15
            uso_pct = np.random.uniform(0.65, 0.95)
        else:
            # Uso >= 95% y M1 >= 15
            uso_pct = np.random.uniform(0.96, 1.08)
            m1 = np.random.randint(16, 45)
            m2 = np.random.randint(0, 25)

        saldo = round(limite * uso_pct, 2)
        score = np.random.randint(450, 600)
        minimos = np.random.randint(2, 6)
        records.append(make_account(
            curr_id, score, limite, saldo,
            m1=m1, m2=m2, m3=np.random.randint(0, 20),
            minimos=minimos,
            sobregiros=np.random.choice([1, 2, 3]),
            antiguedad=np.random.randint(8, 40),
            reestructura=0
        ))
        curr_id += 1

    # 5. Segmento Default Severo (Knock-out R1)
    for _ in range(n_default):
        limite = np.random.choice([12000, 25000, 50000])
        variante = np.random.choice(["mora90", "reestructura_mora"])
        if variante == "mora90":
            m1 = np.random.randint(90, 180)
            m2 = np.random.randint(60, 120)
            reestructura = np.random.choice([0, 1])
        else:
            reestructura = 1
            m1 = np.random.randint(31, 75)
            m2 = np.random.randint(15, 45)

        uso_pct = np.random.uniform(0.85, 1.15)
        saldo = round(limite * uso_pct, 2)
        score = np.random.randint(300, 480)
        records.append(make_account(
            curr_id, score, limite, saldo,
            m1=m1, m2=m2, m3=np.random.randint(10, 60),
            minimos=np.random.randint(3, 10),
            sobregiros=np.random.choice([1, 2, 4]),
            antiguedad=np.random.randint(6, 60),
            reestructura=reestructura
        ))
        curr_id += 1

    df = pd.DataFrame(records)
    # Desordenar aleatoriamente las filas para simular llegada natural de cartera
    df = df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    sample_df = generate_synthetic_portfolio(2500)
    sample_path = os.path.join("data", "raw", "cartera_clientes_simulada.csv")
    sample_df.to_csv(sample_path, index=False)
    print(f"Dataset sintético generado exitosamente: {sample_path} con {len(sample_df)} cuentas.")
