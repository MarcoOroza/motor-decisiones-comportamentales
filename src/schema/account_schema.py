"""
Módulo de Contratos y Validación de Datos (Pydantic Schema).
Alineado con el Diccionario de Variables Comportamentales (Sección 3 del Proyecto).
"""

from typing import List, Tuple, Optional
from pydantic import BaseModel, Field, field_validator
import pandas as pd


class AccountRecord(BaseModel):
    """Contrato de validación estricta para una cuenta crediticia individual."""
    
    ID_CLIENTE: str = Field(..., description="Identificador único del acreditado")
    ID_CONTRATO: str = Field(..., description="Identificador único del contrato de tarjeta/línea")
    LIMITE_CREDITO_ACTUAL: float = Field(..., ge=500.0, description="Línea de crédito autorizada vigente en MXN")
    SALDO_ACTUAL: float = Field(..., ge=0.0, description="Saldo deudor insoluto a la fecha de corte")
    DIAS_ATRASO_M1: int = Field(..., ge=0, description="Días de atraso en el mes inmediato anterior (M1)")
    DIAS_ATRASO_M2: int = Field(..., ge=0, description="Días de atraso reportados hace dos meses (M2)")
    DIAS_ATRASO_M3: int = Field(..., ge=0, description="Días de atraso reportados hace tres meses (M3)")
    PAGOS_MINIMOS_CONSECUTIVOS: int = Field(..., ge=0, le=36, description="Meses consecutivos amortizando sólo el pago mínimo")
    NUM_SOBREGIROS_U6M: int = Field(..., ge=0, le=12, description="Número de sobregiros en los últimos 6 meses")
    SCORE_COMPORTAMENTAL: int = Field(..., ge=300, le=850, description="Score crediticio comportamental interno")
    ANTIGUEDAD_CUENTA_MESES: int = Field(..., ge=1, description="Antigüedad de la cuenta en meses")
    FLAG_REESTRUCTURA_PREVIA: int = Field(..., ge=0, le=1, description="Bandera de reestructura previa (0: No, 1: Sí)")
    PORC_USO_LINEA: Optional[float] = Field(None, ge=0.0, description="Porcentaje de utilización de la línea [0, 100+]")

    @field_validator("FLAG_REESTRUCTURA_PREVIA")
    @classmethod
    def validate_flag(cls, v: int) -> int:
        if v not in (0, 1):
            raise ValueError("FLAG_REESTRUCTURA_PREVIA debe ser 0 o 1")
        return v


def validate_portfolio_df(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Valida la calidad y consistencia del DataFrame de cartera.
    Retorna el DataFrame sanitizado y una lista de advertencias o errores.
    """
    warnings: List[str] = []
    required_cols = [
        "ID_CLIENTE", "ID_CONTRATO", "LIMITE_CREDITO_ACTUAL", "SALDO_ACTUAL",
        "DIAS_ATRASO_M1", "DIAS_ATRASO_M2", "DIAS_ATRASO_M3",
        "PAGOS_MINIMOS_CONSECUTIVOS", "NUM_SOBREGIROS_U6M",
        "SCORE_COMPORTAMENTAL", "ANTIGUEDAD_CUENTA_MESES", "FLAG_REESTRUCTURA_PREVIA"
    ]
    
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"El conjunto de datos carece de las siguientes columnas obligatorias: {missing_cols}")

    df_clean = df.copy()

    # Coerción y verificación de tipos numéricos
    numeric_cols = [
        "LIMITE_CREDITO_ACTUAL", "SALDO_ACTUAL", "DIAS_ATRASO_M1", "DIAS_ATRASO_M2",
        "DIAS_ATRASO_M3", "PAGOS_MINIMOS_CONSECUTIVOS", "NUM_SOBREGIROS_U6M",
        "SCORE_COMPORTAMENTAL", "ANTIGUEDAD_CUENTA_MESES", "FLAG_REESTRUCTURA_PREVIA"
    ]
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")

    # Detección de nulos
    null_counts = df_clean[numeric_cols].isnull().sum()
    null_cols = null_counts[null_counts > 0]
    if not null_cols.empty:
        warnings.append(f"Se detectaron y rellenaron valores nulos en: {dict(null_cols)}")
        df_clean["LIMITE_CREDITO_ACTUAL"] = df_clean["LIMITE_CREDITO_ACTUAL"].fillna(5000.0)
        df_clean["SALDO_ACTUAL"] = df_clean["SALDO_ACTUAL"].fillna(0.0)
        df_clean["DIAS_ATRASO_M1"] = df_clean["DIAS_ATRASO_M1"].fillna(0).astype(int)
        df_clean["DIAS_ATRASO_M2"] = df_clean["DIAS_ATRASO_M2"].fillna(0).astype(int)
        df_clean["DIAS_ATRASO_M3"] = df_clean["DIAS_ATRASO_M3"].fillna(0).astype(int)
        df_clean["PAGOS_MINIMOS_CONSECUTIVOS"] = df_clean["PAGOS_MINIMOS_CONSECUTIVOS"].fillna(0).astype(int)
        df_clean["NUM_SOBREGIROS_U6M"] = df_clean["NUM_SOBREGIROS_U6M"].fillna(0).astype(int)
        df_clean["SCORE_COMPORTAMENTAL"] = df_clean["SCORE_COMPORTAMENTAL"].fillna(600).astype(int)
        df_clean["ANTIGUEDAD_CUENTA_MESES"] = df_clean["ANTIGUEDAD_CUENTA_MESES"].fillna(12).astype(int)
        df_clean["FLAG_REESTRUCTURA_PREVIA"] = df_clean["FLAG_REESTRUCTURA_PREVIA"].fillna(0).astype(int)

    # Asegurar límites lógicos en tipos
    df_clean["SCORE_COMPORTAMENTAL"] = df_clean["SCORE_COMPORTAMENTAL"].clip(lower=300, upper=850)
    df_clean["FLAG_REESTRUCTURA_PREVIA"] = df_clean["FLAG_REESTRUCTURA_PREVIA"].clip(lower=0, upper=1)
    df_clean["LIMITE_CREDITO_ACTUAL"] = df_clean["LIMITE_CREDITO_ACTUAL"].clip(lower=500.0)
    df_clean["SALDO_ACTUAL"] = df_clean["SALDO_ACTUAL"].clip(lower=0.0)

    return df_clean, warnings
