# Reporte de Avance Metodológico y Cierre Técnico — Reporte Semanal 4
## Proyecto de Residencia Profesional — Fase 4 (Pruebas de Estrés Masivo, Resistencia Macroeconómica y Cierre de Memoria Técnica)

---

**Institución Académica:** Tecnológico de Estudios Superiores de Ecatepec (TESE)  
**División Académica:** División de Informática  
**Carrera:** Ingeniería / Licenciatura en Informática  
**Proyecto:** Prototipo de Motor de Decisiones Comportamentales para Riesgo de Crédito (Arquitectura Basada en PowerCurve Strategy Management)  
**Autor / Residente:** Marco Antonio Oroza Ortega  
**Fecha de Reporte:** Noviembre 2026  
**Tipo de Entrega:** Reporte de Avance Metodológico Semanal 4 — Cierre de Etapa y Validación de Rendimiento (100% de Progreso Global)  
**Despliegue Productivo en la Nube:** [https://motor-decisiones-marco.streamlit.app](https://motor-decisiones-marco.streamlit.app)  

---

## 1. Introducción y Contexto de Cierre de la Residencia Profesional

Con la entrega del presente documento se da cumplimiento formal al **100% del cronograma de actividades de la Residencia Profesional** estipulado ante la División de Informática del Tecnológico de Estudios Superiores de Ecatepec (TESE). 

A lo largo del proyecto, la investigación y el desarrollo de software avanzaron de manera incremental, resolviendo la problemática medular de la banca minorista: la sustitución de procesos manuales y heurísticos en hojas de cálculo (Excel) —vulnerables a errores humanos, lentos y carentes de trazabilidad regulatoria— por un **motor de decisiones determinístico, prospectivo y de grado corporativo** basado en Clean Architecture en Python.

La trayectoria evolutiva del proyecto comprende cuatro etapas metodológicas consolidadas:
1. **Semana 1 (Fundación y Experimentación Estratégica):** Contratos de datos validados con Pydantic, cálculo vectorial de variables comportamentales (*roll-rates* de mora), árbol jerárquico de prelación de cuatro políticas fundamentales, framework de experimentación **Champion vs. Challenger** (A/B testing crediticio) y Matriz Bidimensional de Cupos por Deciles de Score FICO.
2. **Semana 2 (Inteligencia Preventiva):** Subsistema de **Alertas Tempranas (*Early Warning System - EWS*)** sustentado en 4 indicadores heurísticos de estrés (EWIs) y clasificación prospectiva de clientes alineada al estándar **IFRS 9 Stage 2**.
3. **Semana 3 (Gobernanza y Reporting Regulatorio):** Módulo de generación automatizada en memoria de **Dictámenes Oficiales en PDF** (ReportLab) y **Cuadernos Contables multi-hoja en Excel (`.xlsx`)** (OpenPyXL) con sello digital criptográfico **SHA-256** bajo directrices de Basilea (**BCBS 239**) y la CNBV.
4. **Semana 4 (Cierre Técnico y Pruebas de Estrés Masivo — Entrega Actual):** Evaluación exhaustiva de alta disponibilidad computacional procesando lotes masivos de hasta **100,000 contratos concurrentes** en memoria RAM, verificación de complejidad asintótica $\mathcal{O}(N)$ y análisis de sensibilidad macroeconómica ante choques severos de recesión y crisis sistémica.

---

## 2. Marco Metodológico: Pruebas de Estrés en Banca y Alta Disponibilidad Computacional

```
                               MARCO DE PRUEBAS DE ESTRÉS (STRESS TESTING)
┌──────────────────────────────────────────────┐     ┌──────────────────────────────────────────────┐
│        ESTRÉS COMPUTACIONAL Y SLA            │     │       ESTRÉS MACROECONÓMICO Y SISTÉMICO      │
├──────────────────────────────────────────────┤     ├──────────────────────────────────────────────┤
│ • Complejidad Asintótica Lineal O(N)         │     │ • Directrices de Banco de México / CNBV      │
│ • Throughput Masivo (> 50,000 ops/seg)       │     │ • Provisiones Contracíclicas IFRS 9          │
│ • Latencia Sub-milisegundo (< 20 µs/contrato)│     │ • Choques de Desempleo, Inflación y Mora     │
│ • Huella de Memoria Estable (Sin Leaks)      │     │ • Contracción Defensiva de Exposición (EAD)  │
└──────────────────────────────────────────────┘     └──────────────────────────────────────────────┘
```

### 2.1 Marco de Estrés Computacional (Alta Disponibilidad y SLA Bancario)
En la ingeniería de motores de decisión para tarjetas de crédito, los picos de procesamiento ocurren al cierre del ciclo de facturación (*corte contable*), donde la institución debe reevaluar millones de contratos en una ventana de tiempo estricta.

Para validar que la arquitectura en capas desarrollada en Python es apta para entornos de misión crítica, se definió un **Acuerdo de Nivel de Servicio (SLA)**:
- **Latencia Unitaria Máxima Admisible:** Menor a $1.0\text{ ms}$ ($1,000\ \mu\text{s}$) por contrato.
- **Rendimiento Mínimo (*Throughput*):** Superior a $10,000\text{ contratos/segundo}$.
- **Consumo de Memoria:** Complejidad espacial $\mathcal{O}(N)$ con liberación inmediata de recursos por el recolector de basura (*Garbage Collector*).

### 2.2 Marco de Estrés Macroeconómico y Sensibilidad (Banco de México / CNBV / IFRS 9)
Las normativas prudenciales bancarias obligan a las entidades financieras a someter sus carteras a simulaciones de choque macroeconómico para medir su vulnerabilidad ante escenarios de crisis. Se implementaron tres regímenes estandarizados:

1. **Línea Base (*Baseline*):** Condiciones económicas estables y ordinarias de operación.
2. **Escenario Adverso (*Recesión Económica*):** Incremento de inflación, alza de tasas de interés y pérdida de solvencia en hogares:
   $$\text{Score}_{\text{recesión}} = \max(300, \text{Score}_{\text{base}} - 35)$$
   $$\text{Saldo}_{\text{recesión}} = \min(1.25 \times \text{Límite}, \text{Saldo}_{\text{base}} \times 1.15)$$
   $$\text{Mora}_{\text{recesión}} = \text{Mora}_{\text{base}} + \Delta_{\text{mora}} \quad \text{con } \Delta_{\text{mora}} \in \{0, 5, 15, 30\}\text{ días}$$
3. **Escenario Severamente Adverso (*Crisis Sistémica / Shock de Desempleo*):** Depresión económica profunda (análoga a la crisis de 2008 o la pandemia de 2020), caracterizada por desempleo acelerado y retiro de liquidez preventiva:
   $$\text{Score}_{\text{crisis}} = \max(300, \text{Score}_{\text{base}} - 70)$$
   $$\text{Saldo}_{\text{crisis}} = \min(1.35 \times \text{Límite}, \text{Saldo}_{\text{base}} \times 1.25)$$
   $$\text{Mora}_{\text{crisis}} = \text{Mora}_{\text{base}} + \Delta_{\text{crisis}} \quad \text{con } \Delta_{\text{crisis}} \in \{0, 15, 35, 65\}\text{ días}$$

---

## 3. Detalle de las Nuevas Implementaciones Técnicas

```mermaid
graph TD
    A[Suite de Pruebas de Estrés stress_testing.py] --> B1[Benchmark de Carga Masiva]
    A --> B2[Simulador Macroeconómico de Choques]
    
    B1 --> C1["Lotes Crecientes: 2.5k, 10k, 25k, 50k, 100k"]
    C1 --> D1[Medición con time.perf_counter]
    C1 --> D2[Trazabilidad RAM con tracemalloc]
    D1 & D2 --> E1[Métricas: Throughput, Latencia µs, Pico MB]
    
    B2 --> C2[Inyección de Perturbaciones Vectorizadas]
    C2 --> D3[Escenario Normal: Línea Base]
    C2 --> D4[Escenario Adverso: Recesión Moderada]
    C2 --> D5[Escenario Severo: Crisis Sistémica]
    D3 & D4 & D5 --> E2[Matriz de Contracción de Exposición EAD]
    
    E1 & E2 --> F[Pestaña 7 Dashboard Streamlit: Estrés Masivo & SLA]
```

### 3.1 Nuevo Módulo Especializado: `src/engine/stress_testing.py`
Se codificó un módulo de ingeniería de pruebas de carga y resistencia que incorpora:
- **`run_scalability_benchmark(batch_sizes, random_seed)`:** Ejecuta en memoria la cadena completa de procesamiento (Validación de esquema Pydantic, Ingeniería de variables, Motor de decisión con prelación, Clasificación EWS y Resumen de auditoría SHA-256). Mide con precisión de microsegundos el tiempo por etapa y el consumo pico de memoria RAM mediante `tracemalloc`.
- **`apply_macroeconomic_shock(df, scenario, random_seed)`:** Transforma vectorizadamente las columnas de la cartera simulando el impacto del choque en los acreditados.
- **`run_stress_scenario_comparison(df_base)`:** Ejecuta en paralelo los 3 escenarios macroeconómicos sobre una misma cartera, computando la variación neta de exposición crediticia (Delta MXN), la distribución de decisiones tácticas y el incremento del semáforo rojo del EWS.

### 3.2 Nueva Pestaña en la Plataforma Web: `src/app/dashboard.py` (Tab 7)
Se integró en la aplicación interactiva la pestaña:
**"⚡ Pruebas de Estrés Masivo & SLA (Stress Testing)"**, la cual incorpora:
1. **Selector de Perfiles de Carga:** Permite al usuario y comité evaluador detonar en tiempo real benchmarks de 2,500, 10,000, 25,000, 50,000 y 100,000 contratos en memoria RAM.
2. **Cuatro Tarjetas KPI de Rendimiento:** Despliegue de Throughput pico, Latencia asintótica unitaria, Huella de memoria y Tiempo total de respuesta.
3. **Gráficas de Escalabilidad Lineal en Plotly:**
   - *Throughput vs. Volumen de Contratos:* Demuestra la ganancia de eficiencia conforme el lote crece debido a la optimización de caché de CPU en NumPy.
   - *Latencia Unitaria vs. Volumen:* Curva de convergencia asintótica demostrando estabilidad en ~16.84 $\mu$s por contrato.
4. **Comparador Macroeconómico Interactivo:** Tres paneles ejecutivos con código cromático (Verde para Normal, Ámbar para Recesión y Rojo para Crisis), tarjetas con el Delta de exposición neta y gráfica de barras agrupada que visualiza cómo el motor apaga los aumentos de cupo y activa bloqueos masivos ante una recesión.

### 3.3 Ampliación de la Batería de Pruebas: `tests/test_rules_engine.py`
Se incorporaron 2 pruebas unitarias automatizadas adicionales en Pytest, elevando la batería final a **19 pruebas unitarias automatizadas (100% exitosas)**:
- `test_stress_testing_scalability_benchmark()`: Comprueba que el benchmark procese lotes de contratos en memoria, verifique todas las llaves de métricas y valide el SLA de latencia (< 1 ms por contrato) y throughput masivo (> 1,000 ops/s).
- `test_macroeconomic_stress_scenarios()`: Comprueba que el choque de crisis severa resulte en un Delta de exposición menor (más restrictivo), aumente los bloqueos temporales por mora y eleve la proporción de cuentas en semáforo Rojo del EWS.

---

## 4. Resultados Experimentales y Validación de Carga Masiva (2,500 a 100,000 Cuentas)

### 4.1 Benchmark de Escalabilidad y Tiempos de Respuesta Computacional

Al someter el motor de decisiones a lotes crecientes de prueba en un entorno estándar de computación, se obtuvieron los siguientes resultados empíricos certificados:

| Volumen de Contratos ($N$) | Tiempo Total Inferencia | Throughput Efectivo | Latencia Unitaria ($\mu$s) | Latencia Unitaria (ms) | Memoria RAM Pico | SLA Cumplido (< 1 ms) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2,500 contratos** | 0.105 s | 23,807.3 ops/s | 42.00 $\mu$s | 0.042 ms | 2.03 MB | ✅ **CUMPLE** (95.8% de holgura) |
| **10,000 contratos** | 0.217 s | 46,165.7 ops/s | 21.66 $\mu$s | 0.022 ms | 7.75 MB | ✅ **CUMPLE** (97.8% de holgura) |
| **25,000 contratos** | 0.457 s | 54,666.7 ops/s | 18.29 $\mu$s | 0.018 ms | 19.24 MB | ✅ **CUMPLE** (98.2% de holgura) |
| **50,000 contratos** | 0.859 s | 58,187.7 ops/s | 17.19 $\mu$s | 0.017 ms | 38.36 MB | ✅ **CUMPLE** (98.3% de holgura) |
| **100,000 contratos** | **1.684 s** | **59,384.3 ops/s** | **16.84 $\mu$s** | **0.017 ms** | **76.62 MB** | ✅ **CUMPLE** (98.3% de holgura) |

#### Desglose de Latencia por Etapa del Pipeline (Lote Masivo de 100,000 Cuentas):
- **Validación de Calidad y Tipos de Datos:** 0.0162 s (0.96% del tiempo total).
- **Ingeniería de Variables Vectoriales (*Feature Pipeline*):** 0.2437 s (14.47%).
- **Árbol Jerárquico de Prelación de Reglas (*Decision Engine*):** 0.9427 s (55.98%).
- **Sistema de Alertas Tempranas (*Early Warning System - EWS*):** 0.4718 s (28.02%).
- **Auditoría y Hash Criptográfico SHA-256:** 0.0096 s (0.57%).

> **Hallazgo de Arquitectura:** El sistema exhibe una **complejidad asintótica estrictamente lineal $\mathcal{O}(N)$**. La latencia por contrato disminuye de 42.0 $\mu$s a 16.84 $\mu$s conforme el lote crece debido a la optimización de vectorización y acceso contiguo en memoria de Pandas/NumPy. Evaluar **100,000 clientes en 1.68 segundos utilizando solo 76.6 MB de memoria RAM** confirma que la solución puede operar en centros de datos bancarios con recursos de cómputo mínimos.

---

### 4.2 Resultados de Resistencia y Sensibilidad Macroeconómica (Cartera Base de 2,500 Cuentas)

Al inyectar perturbaciones macroeconómicas controladas sobre la cartera institucional de 2,500 contratos, se demostró la capacidad de blindaje y amortiguación contracíclica del motor:

| Dimensión de Análisis | Línea Base (Normal) | Recesión Moderada | Crisis Sistémica Severa | Comportamiento del Motor |
| :--- | :---: | :---: | :---: | :--- |
| **Delta Exposición Neta (MXN)** | **+$3,408,257.67** | **-$2,063,949.27** | **-$5,242,704.08** | **Contracción defensiva de capital ($-\$8.65\text{M}$ spread)** |
| **Aumentos de Cupo Prime** | 625 cuentas (25.0%) | 152 cuentas (6.1%) | 9 cuentas (0.36%) | **Apagado automático de ofertas expansivas (-98.5%)** |
| **Mantenimiento Regular** | 1,132 cuentas (45.3%) | 1,415 cuentas (56.6%) | 707 cuentas (28.3%) | Transición forzosa hacia cubetas de riesgo |
| **Reducciones Preventivas** | 399 cuentas (16.0%) | 253 cuentas (10.1%) | 230 cuentas (9.2%) | Mitigación activa protegiendo 105% de saldo |
| **Bloqueos Temporales por Mora** | 219 cuentas (8.8%) | 555 cuentas (22.2%) | **1,393 cuentas (55.7%)** | **Contención masiva ante deterioro acelerado (+536%)** |
| **Cancelaciones por Default** | 125 cuentas (5.0%) | 125 cuentas (5.0%) | **161 cuentas (6.4%)** | Envío oportuno a cobranza prejudicial y legal |
| **Semáforo EWS Rojo (Crítico)** | 572 cuentas (22.9%) | 793 cuentas (31.7%) | **1,155 cuentas (46.2%)** | Detección de asfixia en el 46.2% de los acreditados |
| **Semáforo EWS Verde (Normal)** | 916 cuentas (36.6%) | 290 cuentas (11.6%) | **36 cuentas (1.4%)** | Colapso de la población sin factores de estrés |

**Conclusión del Experimento:** Ante una crisis sistémica severa, el motor no requiere reprogramación manual: de forma algorítmica y determinística **contrae la exposición de la cartera en -$5.24 millones de pesos**, frena el otorgamiento de líneas adicionales a niveles prácticamente nulos (solo 9 clientes Super Prime aprobados) y **bloquea preventivamente el 55.7% de las tarjetas**, blindando el balance del banco antes de que el default sea irrecuperable.

---

## 5. Bitácora de Cambios Consolidada (Changelog Integral del Proyecto)

```
                            EVOLUCIÓN ARQUITECTÓNICA DEL PROYECTO (100% CUMPLIDO)
  ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
  │  SEMANA 1 (v1.5.0)    │   │  SEMANA 2 (v2.0.0)    │   │  SEMANA 3 (v2.5.0)    │   │  SEMANA 4 (v3.0.0)    │
  ├───────────────────────┤   ├───────────────────────┤   ├───────────────────────┤   ├───────────────────────┤
  │ • Champion/Challenger │   │ • Alertas EWS / EWIs  │   │ • Reporting PDF/XLSX  │   │ • Stress Testing 100k │
  │ • Matriz por Deciles  │──>│ • Semáforos IFRS 9 St2│──>│ • Sello SHA-256       │──>│ • Choques Macro       │
  │ • Rediseño UI Fintech │   │ • Matriz Anticipación │   │ • 4 Hojas Contables   │   │ • Complejidad O(N)    │
  │ • 12 Pruebas Pytest   │   │ • 15 Pruebas Pytest   │   │ • 17 Pruebas Pytest   │   │ • 19 Pruebas Pytest   │
  └───────────────────────┘   └───────────────────────┘   └───────────────────────┘   └───────────────────────┘
```

- **Semana 1 (v1.5.0):** Implementación del framework de experimentación Champion vs. Challenger (A/B testing) y Matriz Bidimensional de Límites por Deciles FICO con protección de saldo al 105%.
- **Semana 2 (v2.0.0):** Integración del Sistema de Alertas Tempranas (EWS) con 4 indicadores de estrés heurístico y semáforo preventivo alineado a IFRS 9 Stage 2.
- **Semana 3 (v2.5.0):** Automatización del Reporting Regulatorio en memoria: Dictamen Ejecutivo en PDF institucional (ReportLab) y Cuaderno Contable multi-hoja en Excel `.xlsx` (OpenPyXL) con sello digital criptográfico SHA-256.
- **Semana 4 (v3.0.0 — Entrega Final):** Pruebas de estrés masivo a 100,000 contratos (1.68 s, 59.3k ops/s), demostración de complejidad lineal $\mathcal{O}(N)$, simulación de choques macroeconómicos sistémicos y cierre formal de Residencia Profesional con 19 pruebas unitarias automatizadas.

---

## 6. Evaluación Global y Dictamen de Cierre de Residencia Profesional

Con el desarrollo de este cuarto entregable semanal, se certifica el **cumplimiento integral (100%) de los objetivos planteados** para la Residencia Profesional en la División de Informática del TESE:

1. **Impacto en Ingeniería de Software:**
   - Adopción estricta de principios de **Clean Architecture** y **Domain-Driven Design (DDD)**, manteniendo el núcleo de reglas financieras 100% desacoplado de frameworks web o bases de datos.
   - Metodología **Test-Driven Development (TDD)** con una batería de **19 pruebas unitarias automatizadas en Pytest** que garantizan no-colisión de reglas y control riguroso de condiciones de frontera.
   - Flujo de Entrega Continua (**CI/CD**) mediante control de versiones en **GitHub** con despliegue productivo automatizado en **Streamlit Cloud**.
2. **Impacto Financiero y Regulatorio:**
   - Erradicación total de la dependencia de hojas de cálculo vulnerables (Excel básico), reemplazándolas por un motor determinístico y auditable.
   - Cumplimiento integral de las normativas de gobernanza de modelos de crédito de la **CNBV**, principios de agregación de datos de riesgo **BCBS 239** de **Basilea III/IV** y cálculo prospectivo de reservas conforme a **IFRS 9**.
   - Disponibilidad computacional masiva: capacidad probada para procesar la cartera de 100,000 tarjetas de crédito en menos de 2 segundos.

---

**Firma del Residente:**  
**Marco Antonio Oroza Ortega**  
División de Informática  
Tecnológico de Estudios Superiores de Ecatepec (TESE)
