# Motor de Decisiones Comportamentales para Riesgo de Crédito
## (Arquitectura Basada en Experian PowerCurve Strategy Management)

**Proyecto de Residencia Profesional**  
- **Autor / Residente:** Marco Antonio Oroza Ortega  
- **Institución Académica:** Tecnológico de Estudios Superiores de Ecatepec (TESE)  
- **División Académica:** División de Informática  
- **Versión:** 2.0.0 (Fase 2: Champion/Challenger y Sistema de Alertas Tempranas EWS)  
- **Despliegue Productivo en la Nube:** [https://motor-decisiones-marco.streamlit.app](https://motor-decisiones-marco.streamlit.app)  

---

## 📌 Descripción del Proyecto
Este sistema emula las capacidades clave de un **Motor de Decisiones de Estrategia Crediticia** (*PowerCurve Strategy Management*), especializado en la gestión del comportamiento de cartera (*Account Management* / Tarjetas de Crédito).

Reemplaza los métodos manuales y vulnerables en hojas de cálculo (Excel) mediante una arquitectura modular, auditable y determinística capaz de evaluar miles de contratos bancarios en segundos, asignando acciones estratégicas y códigos de razón (*Reason Codes*) conforme a normativas de la CNBV, Basilea III y la norma IFRS 9.

---

## 🏗️ Arquitectura del Sistema
El prototipo implementa una arquitectura en capas desacopladas (Clean Architecture / DDD):
1. **`src/schema/account_schema.py`:** Contratos y validación de tipos con Pydantic y Pandas.
2. **`src/pipeline/feature_engineering.py`:** Cálculo de variables comportamentales (ratios de utilización, roll rates de mora intermensual, deltas).
3. **`src/engine/rules.py`:** Implementación formal de las 4 políticas de riesgo (Knock-out, Contención, Mitigación, Expansión) y Matriz Dinámica por Deciles.
4. **`src/engine/strategy_manager.py`:** Orquestador de prelación jerárquica (*Precedence Tree*) para evitar colisiones lógicas.
5. **`src/engine/champion_challenger.py`:** Simulador de A/B Testing crediticio y partición estocástica de cartera.
6. **`src/engine/early_warning.py`:** Sistema de Alertas Tempranas (EWS) con 4 indicadores de estrés anticipado (IFRS 9 Stage 2).
7. **`src/engine/audit.py`:** Generador del log inmutable de auditoría para comités de riesgo.
8. **`src/app/dashboard.py`:** Dashboard analítico e interactivo en Streamlit con 6 pestañas ejecutivas, velocímetro FICO y expediente 360°.
9. **`tests/test_rules_engine.py`:** Batería de 15 pruebas unitarias y de estrés con Pytest (100% exitosas).

---

## 🚀 Guía de Puesta en Marcha

### 1. Activar el Entorno Virtual
En la terminal de PowerShell dentro de la carpeta del proyecto:
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Ejecutar la Suite de Pruebas Unitarias
Para validar que el motor cumple todas las reglas, condiciones frontera, matriz de deciles y alertas tempranas:
```powershell
.\.venv\Scripts\pytest.exe -v
```

### 3. Iniciar el Dashboard Interactivo (Streamlit)
Para abrir la interfaz gráfica ejecutiva en el navegador local:
```powershell
.\.venv\Scripts\streamlit.exe run src/app/dashboard.py
```
El panel se abrirá automáticamente en `http://localhost:8501`.

---

## 📊 Reglas de Negocio y Sistema de Alertas Tempranas (EWS)

| Prioridad | Módulo / Regla | Condición Lógica Clave | Acción Resultante | Código de Razón |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **Knock-out Severo** | Mora $M1 \ge 90$ días o Reestructura con $M1 \ge 30$ días | `CANCELAR_LINEA_Y_ENVIO_COBRANZA` (Límite = $0.0) | `RC_DEFAULT_SEVERO_IFRS9` |
| **2** | **Contención Inmediata** | Mora creciente $M1 \ge 30$ y $M1 > M2$, o Uso $\ge 95\%$ con mora $\ge 15$ d | `BLOQUEO_TEMPORAL_LINEA` (Tarjeta suspendida) | `RC_DETERIORO_MORA_ROLLFORWARD_CRITICO` |
| **3** | **Mitigación Preventiva** | Score $< 580$ con Uso $\ge 80\%$, o $\ge 4$ mínimos con Score $< 620$ | `REDUCIR_LINEA_PREVENTIVA` (Reducción escalonada) | `RC_ESTRES_FINANCIERO_PAGOS_MINIMOS_PERSISTENTES` |
| **4** | **Expansión Proactiva** | Score $\ge 720$, 0 mora, Uso 40-75%, Antigüedad $\ge 12$m, 0 sobregiros | `INCREMENTAR_LINEA_PROACTIVO` (Matriz +15% a +35%) | `RC_CLIENTE_PRIME_EXCELENTE_HISTORIAL` |
| **5** | **Mantenimiento** | Comportamiento dentro de tolerancia estándar | `MANTENER_CONDICIONES_ACTUALES` (Sin cambio) | `RC_PERFIL_DENTRO_DE_TOLERANCIA_ESTANDAR` |
| **EWS** | **Alertas Tempranas** | 4 EWIs (Uso $\ge 85\%$, $\ge 2$ mínimos, mora 1-29d, sobregiros) | Semáforos Verde, Amarillo, Naranja, Rojo | Acciones preventivas IFRS 9 Stage 2 |

---

## 📁 Estructura del Repositorio
```text
Proyecto Residencias/
├── 01_Documentacion_Tecnica_Conceptual.md  # Reporte técnico conceptual (Fase 1)
├── 02_Avance_Metodologico_e_Implementaciones.md # Reporte de avance semanal 1
├── 03_Avance_Metodologico_Semanal_2.md     # Reporte de avance semanal 2 (EWS)
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
│   │   ├── champion_challenger.py          # Simulador Champion/Challenger (A/B testing)
│   │   ├── early_warning.py                # Sistema de Alertas Tempranas (EWS)
│   │   └── audit.py                        # Trazabilidad y métricas
│   └── app/dashboard.py                    # Interfaz Streamlit Fintech
└── tests/
    └── test_rules_engine.py                # 15 pruebas unitarias con Pytest (100% pass)
```
