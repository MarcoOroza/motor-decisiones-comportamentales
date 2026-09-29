# Motor de Decisiones Comportamentales para Riesgo de Crédito
## (Arquitectura Basada en Experian PowerCurve Strategy Management)

**Proyecto de Residencia Profesional**  
- **Autor / Residente:** Marco Antonio Oroza Ortega  
- **Institución Académica:** Tecnológico de Estudios Superiores de Ecatepec (TESE)  
- **División Académica:** División de Informática  
- **Versión:** 1.0.0 (Prototipo Funcional de Primer Avance)

---

## 📌 Descripción del Proyecto
Este sistema emula las capacidades clave de un **Motor de Decisiones de Estrategia Crediticia** (*PowerCurve Strategy Management*), especializado en la gestión del comportamiento de cartera (*Account Management* / Tarjetas de Crédito).

Reemplaza los métodos manuales y vulnerables en hojas de cálculo (Excel) mediante una arquitectura modular, auditable y determinística capaz de evaluar miles de contratos bancarios en segundos, asignando acciones estratégicas y códigos de razón (*Reason Codes*) conforme a normativas de la CNBV y Basilea III/IV.

---

## 🏗️ Arquitectura del Sistema
El prototipo implementa una arquitectura en capas desacopladas:
1. **`src/schema/account_schema.py`:** Contratos y validación de tipos con Pydantic y Pandas.
2. **`src/pipeline/feature_engineering.py`:** Cálculo de variables comportamentales (ratios de utilización, roll rates de mora intermensual, deltas).
3. **`src/engine/rules.py`:** Implementación formal de las 4 políticas de riesgo (Knock-out, Contención, Mitigación, Expansión) y la política residual.
4. **`src/engine/strategy_manager.py`:** Orquestador de prelación jerárquica (*Precedence Tree*) para evitar colisiones lógicas.
5. **`src/engine/audit.py`:** Generador del log inmutable de auditoría para comités de riesgo.
6. **`src/app/dashboard.py`:** Dashboard analítico e interactivo en Streamlit con gráficos de impacto financiero y explorador 360° de cuentas.
7. **`tests/test_rules_engine.py`:** Batería de pruebas unitarias y de estrés con Pytest.

---

## 🚀 Guía de Puesta en Marcha

### 1. Activar el Entorno Virtual
En la terminal de PowerShell dentro de la carpeta del proyecto:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Ejecutar la Suite de Pruebas Unitarias
Para validar que el motor cumple todas las reglas, condiciones frontera y prelación:
```powershell
.\.venv\Scripts\pytest.exe -v
```

### 3. Iniciar el Dashboard Interactivo (Streamlit)
Para abrir la interfaz gráfica ejecutiva en el navegador:
```powershell
.\.venv\Scripts\streamlit.exe run src/app/dashboard.py
```
El panel se abrirá automáticamente en `http://localhost:8501`.

---

## 📊 Reglas de Negocio Implementadas

| Prioridad | Regla | Condición Lógica Clave | Acción Resultante | Código de Razón |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Knock-out Severo** | Mora $M1 \ge 90$ días o Reestructura con $M1 \ge 30$ días | `CANCELAR_LINEA_Y_ENVIO_COBRANZA` (Límite = $0.0) | `RC_DEFAULT_SEVERO_IFRS9` |
| **2** | **Contención Inmediata** | Mora creciente $M1 \ge 30$ y $M1 > M2$, o Uso $\ge 95\%$ con mora $\ge 15$ d | `BLOQUEO_TEMPORAL_LINEA` (Tarjeta suspendida) | `RC_DETERIORO_MORA_ROLLFORWARD_CRITICO` |
| **3** | **Mitigación Preventiva** | Score $< 580$ con Uso $\ge 80\%$, o $\ge 4$ mínimos con Score $< 620$ | `REDUCIR_LINEA_PREVENTIVA` (Reducción al 60%) | `RC_ESTRES_FINANCIERO_PAGOS_MINIMOS_PERSISTENTES` |
| **4** | **Expansión Proactiva** | Score $\ge 720$, 0 mora, Uso 40-75%, Antigüedad $\ge 12$m, 0 sobregiros | `INCREMENTAR_LINEA_PROACTIVO` (+25% de aumento) | `RC_CLIENTE_PRIME_EXCELENTE_HISTORIAL` |
| **5** | **Mantenimiento** | Comportamiento dentro de tolerancia estándar | `MANTENER_CONDICIONES_ACTUALES` (Sin cambio) | `RC_PERFIL_DENTRO_DE_TOLERANCIA_ESTANDAR` |

---

## 📁 Estructura del Repositorio
```text
Proyecto Residencias/
├── 01_Documentacion_Tecnica_Conceptual.md  # Reporte de especificación de Fase 1
├── README.md                               # Manual técnico y de ejecución
├── requirements.txt                        # Dependencias del proyecto
├── data/
│   ├── raw/cartera_clientes_simulada.csv   # Cartera sintética de 2,500 cuentas
│   └── processed/                          # Almacén de decisiones y auditorías
├── src/
│   ├── data_generator.py                   # Generador de poblaciones bancarias
│   ├── schema/account_schema.py            # Contratos de datos
│   ├── pipeline/feature_engineering.py     # Ratios y deltas comportamentales
│   ├── engine/
│   │   ├── rules.py                        # Reglas y políticas parametrizables
│   │   ├── strategy_manager.py             # Árbol de prelación
│   │   └── audit.py                        # Trazabilidad y métricas
│   └── app/dashboard.py                    # Interfaz Streamlit
└── tests/
    └── test_rules_engine.py                # 10 pruebas unitarias con Pytest
```
