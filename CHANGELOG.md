# Bitácora de Versiones del Proyecto (Changelog)
## Prototipo de Motor de Decisiones Comportamentales para Riesgo de Crédito
### (Arquitectura Basada en Experian PowerCurve Strategy Management)

**Institución Académica:** Tecnológico de Estudios Superiores de Ecatepec (TESE)  
**División Académica:** División de Informática  
**Autor / Residente:** Marco Antonio Oroza Ortega  
**Proyecto de Residencia Profesional**  

---

Todas las modificaciones notables y evoluciones metodológicas de este proyecto se documentan en este archivo conforme al estándar *Keep a Changelog*, adaptado para el seguimiento académico y de ingeniería de software.

---

## [2.0.0] - Semana 2 (Octubre 2026) — Alertas Tempranas y Detección Proactiva de Estrés
### 🚀 Agregado (New Features)
- **Módulo `src/engine/early_warning.py`:** Implementación del motor de Alertas Tempranas (`EarlyWarningSystem`) y catálogo formal de definiciones `EWI_CATALOG`.
- **4 Indicadores Heurísticos de Estrés Financiero (EWIs):**
  - `FLAG_EWI_USO`: Detección de apalancamiento crítico (utilización $\ge 85\%$).
  - `FLAG_EWI_MINIMOS`: Detección de fatiga de liquidez ($\ge 2$ pagos mínimos consecutivos).
  - `FLAG_EWI_MORA_INCIPIENTE`: Detección de *roll-forward* temprano ($1 \le \text{Mora} < 30$ días con $M_1 \ge M_2$).
  - `FLAG_EWI_VULNERABILIDAD`: Antecedentes de fragilidad presupuestal ($\ge 1$ sobregiro en últimos 6 meses o reestructura previa).
- **Semáforo Preventivo Graduado:** Asignación automática de los niveles *VERDE_NORMAL*, *AMARILLO_VIGILANCIA*, *NARANJA_MODERADO* y *ROJO_CRITICO*.
- **Acciones Preventivas Estandarizadas:** Dictámenes automáticos de mitigación (`BLOQUEO_PREVENTIVO_Y_CONTACTO_RETENCION`, `REDUCIR_LINEA_Y_RESTRINGIR_SOBREGIROS`, `CONGELAR_OFERTAS_Y_RECORDATORIO_PREVENTIVO`, `MONITOREO_ESTANDAR_SIN_RESTRICCION`).
- **Pestaña 3 en Streamlit ("🚨 Alertas Tempranas - EWS"):**
  - 4 Tarjetas KPI Fintech con participación porcentual del semáforo.
  - Gráfica de dona interactiva con código cromático normativo.
  - Histograma horizontal de frecuencia de indicadores EWIs activados.
  - **Matriz de Anticipación Cruzada:** Tabla cruzada bidimensional entre Nivel EWS y Decisión de Política Tradicional.
  - Padrón filtrable de cuentas bajo vigilancia con exportación de registros.
- **Enriquecimiento del Expediente 360° (Tab 4):** Badge de riesgo EWS y panel de 4 pastillas diagnósticas (*chips*) en tiempo real por cliente inspeccionado.
- **3 Pruebas Unitarias Automatizadas en Pytest:** Cobertura de condiciones individuales, agregación de semáforos y generación de métricas (`tests/test_rules_engine.py`), elevando la batería a 15 pruebas (100% exitosas).

### 💡 Racional Técnico y Financiero (¿Por qué se agregó?)
- **Alineación con Estándares IFRS 9 / Basilea III:** La normativa contable internacional castiga a las entidades bancarias que reservan capital de forma tardía. Exige identificar activamente el **Incremento Significativo del Riesgo de Crédito (SICR - Stage 2)**.
- **Superación de Políticas Reactivas:** Las políticas tradicionales esperan pasivamente a que un cliente acumule mora severa ($\ge 60$ o $90$ días) para recién reducir líneas o cancelar tarjetas, momento en el cual la probabilidad de recuperación desciende a menos del 25%.
- **Capacidad de Anticipación Comprobada:** En la cartera base de 2,500 cuentas, la matriz de anticipación descubrió a **331 clientes en estrés financiero activo (271 en Naranja y 60 en Rojo)** que el motor previo clasificaba como "normales" en `MANTENER_CONDICIONES_ACTUALES`. El EWS permite congelar sobregiros y contactar a estos clientes semanas antes de que incurran en impago formal.

---

## [1.5.0] - Semana 1 (Octubre 2026) — Experimentación Estratégica Champion/Challenger
### 🚀 Agregado (New Features)
- **Módulo `src/engine/champion_challenger.py`:** Clase `ChampionChallengerSimulator` para división estocástica de tráfico A/B y simulación paralela contrafactual (*What-If Analysis*).
- **Matriz Bidimensional de Límites por Deciles (`PolicyParameters.habilitar_matriz_dinamica`):**
  - Incremento escalonado: Super Prime ($\ge 800$) $+35\%$, Prime Alto ($750-799$) $+25\%$, Prime Estándar ($720-749$) $+15\%$.
  - Reducción escalonada: Subprime Severo ($< 520$) al $50\%$, Subprime Moderado ($520-579$) al $65\%$.
  - Algoritmo de salvaguarda de sobregiro técnico: Límite protegido al $105\%$ del saldo insoluto.
- **Pestaña 6 en Streamlit ("🥊 Metodología Champion vs Challenger"):**
  - Selector de políticas retadoras preconfiguradas (*Challenger Conservador*, *Expansivo*, *Anti-Mora*).
  - Control deslizante interactivo de asignación porcentual de tráfico (50/50 a 95/5).
  - Gráfica de barras comparativa de distribución de decisiones entre Champion y Challenger.
- **Rediseño UI/UX Fintech Corporativo:**
  - Tipografía profesional (*Plus Jakarta Sans* y *JetBrains Mono*).
  - Tacómetro interactivo FICO en Plotly con 4 bandas de riesgo (*Subprime*, *Vulnerable*, *Moderado*, *Prime*).
  - Tarjetas de métricas tipo cápsula con elevación suave y micro-animaciones en *hover*.
- **2 Pruebas Unitarias Automatizadas en Pytest:** Validación de matriz de deciles y consistencia de KPIs de partición A/B (12 pruebas en total).

### 💡 Racional Técnico y Financiero (¿Por qué se agregó?)
- **Mitigación de Riesgo Operativo en Despliegue:** En la banca real y en herramientas corporativas tipo Experian PowerCurve, una entidad bancaria jamás implementa un cambio de política directamente sobre el 100% de su cartera. Un cambio imprevisto en los umbrales de score o corte de mora podría generar pérdidas por impago multimillonarias o provocar fuga masiva de clientes solventes por rechazos injustificados.
- **Optimización de Rentabilidad y Capital:** Aplicar incrementos o reducciones con un porcentaje estático plano (e.g. +25% general) desaprovecha el perfil de riesgo del cliente. Un cliente Super Prime amerita mayor apalancamiento (+35%) que uno Prime inicial (+15%), mientras que en reducciones se erradican los sobregiros técnicos artificiales que perjudican innecesariamente el historial crediticio del acreditado.

---

## [1.0.0] - Línea Base Inicial (Septiembre 2026) — Núcleo del Motor de Decisiones
### 🚀 Agregado (New Features)
- **Capa de Contratos y Calidad de Datos (`src/schema/account_schema.py`):** Esquema Pydantic para validación de tipos, rangos numéricos y detección de anomalías.
- **Pipeline de Ingeniería de Variables (`src/pipeline/feature_engineering.py`):** Cómputo vectorizado de ratios de uso de línea, morosidad acumulada y transiciones intermensuales.
- **Árbol Jerárquico de Prelación (`src/engine/rules.py` y `src/engine/strategy_manager.py`):**
  - Regla 1 (Prioridad 1): Knock-Out Severo (Mora $\ge 90$ días o reestructura con mora $\ge 30$ días).
  - Regla 2 (Prioridad 2): Contención Inmediata (*Roll-forward* creciente o uso crítico $\ge 95\%$ con mora $\ge 15$ días).
  - Regla 3 (Prioridad 3): Mitigación Preventiva (Score $< 580$ con uso $\ge 80\%$, o $\ge 4$ pagos mínimos consecutivos).
  - Regla 4 (Prioridad 4): Expansión Proactiva (Score $\ge 720$, 0 mora, uso $40-75\%$, antigüedad $\ge 12$ meses).
  - Regla 0 (Residual): Mantenimiento de condiciones actuales.
- **Módulo de Auditoría y Trazabilidad (`src/engine/audit.py`):** Generación de `execution_id` único, logs inmutables y códigos de razón (*Reason Codes*) estandarizados.
- **Generador de Cartera Bancaria Sintética (`src/data_generator.py`):** Simulación estocástica reproducible de 2,500 cuentas con distribuciones realistas de la banca mexicana.
- **Dashboard Analítico Base (`src/app/dashboard.py`):** Visualizaciones de impacto financiero, cartera decidida y descarga de reportes en CSV y JSON.
- **10 Pruebas Unitarias Automatizadas en Pytest:** Verificación estricta de condiciones de frontera y no-colisión de reglas.

### 💡 Racional Técnico y Financiero (¿Por qué se agregó?)
- **Sustitución de Hojas de Cálculo Vulnerables:** En muchas instituciones financieras menores, la administración de cartera se realiza manualmente mediante macros de Excel, carentes de gobierno de datos, trazabilidad y auditabilidad regulatoria ante la CNBV.
- **Determinismo y Eficiencia:** La arquitectura modular en capas desacopladas garantiza que una cartera de 2,500 cuentas se evalúe de manera determinística, auditable y en menos de un segundo.
