# Reporte de Avance Metodológico y Nuevas Implementaciones
## Proyecto de Residencia Profesional — Fase 2 (Evolución de Estrategias y Experimentación)

---

**Institución Académica:** Tecnológico de Estudios Superiores de Ecatepec (TESE)  
**División Académica:** División de Informática  
**Carrera:** Informática  
**Proyecto:** Prototipo de Motor de Decisiones Comportamentales para Riesgo de Crédito (Arquitectura Basada en PowerCurve Strategy Management)  
**Autor / Residente:** Marco Antonio Oroza Ortega  
**Fecha de Reporte:** Octubre 2026  
**Tipo de Entrega:** Avance de Metodología e Implementación Semanal  

---

## 1. Introducción y Contexto de la Evolución del Proyecto

En el avance inicial del proyecto se resolvió la problemática medular de la banca minorista: la sustitución de procesos manuales y heurísticos en hojas de cálculo (Microsoft Excel) —carentes de trazabilidad, gobierno de datos y auditabilidad— por un **motor de decisiones determinístico** basado en una arquitectura en capas en Python. 

Dicha primera fase sentó las bases operativas:
1. Ingesta estructurada y contratos de calidad de datos mediante Pydantic.
2. Ingeniería de variables comportamentales (ratios de utilización y roll rates de mora).
3. Árbol jerárquico de prelación con cuatro políticas fundamentales (*Knock-out*, *Contención*, *Mitigación*, *Expansión* y *Mantenimiento*).
4. Generación estandarizada de códigos de razón (*Reason Codes*) y dashboard interactivo en Streamlit.

Para este nuevo ciclo de avance semanal, el proyecto evoluciona hacia el **marco metodológico avanzado de toma de decisiones crediticias**. En la industria financiera y en soluciones de misión crítica tipo Experian PowerCurve, una entidad bancaria **nunca** reemplaza una política de crédito de forma directa sobre el 100% de la cartera. Se requiere una metodología rigurosa de experimentación, partición controlada de tráfico y dimensionamiento dinámico del riesgo.

---

## 2. Marco Metodológico Adoptado

El desarrollo implementado en esta etapa se rige bajo dos pilares metodológicos:

```
                            MARCO METODOLÓGICO DEL PROYECTO
┌─────────────────────────────────────────────────┐   ┌─────────────────────────────────────────────────┐
│     METODOLOGÍA DE INGENIERÍA DE SOFTWARE       │   │       METODOLOGÍA DE RIESGO FINANCIERO          │
├─────────────────────────────────────────────────┤   ├─────────────────────────────────────────────────┤
│ • Arquitectura Limpia (Clean Architecture)      │   │ • Framework Champion / Challenger (A/B Testing) │
│ • Diseño Dirigido por el Dominio (DDD)          │   │ • Matriz Bidimensional de Cupos (Matrix Sizing) │
│ • Desarrollo Guiado por Pruebas (TDD / Pytest)  │   │ • Mitigación Controlada de Exposición (EAD)     │
│ • Entrega Continua y Versionado Git             │   │ • Explicabilidad Regulatoria (Basilea / CNBV)   │
└─────────────────────────────────────────────────┘   └─────────────────────────────────────────────────┘
```

### 2.1 Metodología de Ingeniería de Software (Clean Architecture y TDD)
Se profundizó el desacoplamiento de componentes mediante principios de **Clean Architecture**:
- **Capa de Dominio y Reglas:** Funciones puras e independientes de frameworks externos, encargadas de evaluar predicados lógicos financieros.
- **Capa de Orquestación y Estrategia:** Desacoplada de la fuente de datos; recibe contratos validados y asigna tratamientos determinísticos.
- **Capa de Experimentación:** Nuevo módulo que gobierna la partición estocástica de clientes sin alterar el núcleo de reglas.
- **Metodología TDD (Test-Driven Development):** Ningún algoritmo de política se despliega sin pruebas unitarias automatizadas que garanticen la no-colisión de reglas y la consistencia en condiciones frontera (*boundary values*).

### 2.2 Metodología de Riesgo: Framework Champion / Challenger (A/B Testing Crediticio)
La metodología **Champion/Challenger** es el estándar de oro en el diseño estratégico de motores de crédito:
1. **Estrategia Champion (Línea Base Vigente):** Es la política formalmente autorizada y aprobada por el comité de riesgo, aplicada a la mayor parte de la población (típicamente entre 70% y 85% de la cartera).
2. **Estrategia Challenger (Política Retadora):** Es una variante estratégica con hipótesis de optimización (e.g., umbrales de morosidad más tempranos para contener pérdidas, o deciles de score más exigentes para otorgar incrementos).
3. **Mecanismo de Partición Controlada:** Se divide la cartera de forma pseudoaleatoria y determinística para evaluar simultáneamente ambas estrategias sobre clientes homogéneos.
4. **Criterios de Promoción:** Si tras un periodo de simulación la estrategia Challenger demuestra mitigar mayor morosidad sin castigar la rentabilidad de clientes solventes, el comité promueve la política Challenger para convertirse en el nuevo Champion.

### 2.3 Metodología de Asignación Bidimensional de Límites (Matrix Limit Sizing)
En los motores elementales, los aumentos y decrementos de cupo suelen calcularse como un factor estático plano (e.g., +25% general a todos los aprobados). 

En este avance metodológico se implementó una **Matriz de Asignación Escalonada por Deciles**:
* **Expansión Escalonada (Regla 4):**
  - Score Comportamental $\ge 800$ puntos (*Super Prime*): Incremento del **+35%**.
  - Score Comportamental entre $750$ y $799$ puntos (*Prime Alto*): Incremento del **+25%**.
  - Score Comportamental entre $720$ y $749$ puntos (*Prime Estándar*): Incremento del **+15%**.
* **Mitigación Escalonada (Regla 3):**
  - Score Comportamental $< 520$ puntos (*Deterioro Severo*): Reducción de línea al **50%**.
  - Score Comportamental entre $520$ y $579$ puntos (*Fatiga Moderada*): Reducción de línea al **65%**.
  *(En todos los casos protegiendo un colchón del 105% del saldo insoluto para erradicar sobregiros técnicos artificiales).*

---

## 3. Detalle de las Nuevas Implementaciones Técnicas

Durante este ciclo semanal se programaron y agregaron los siguientes componentes al repositorio del proyecto:

### 3.1 Nuevo Módulo: `src/engine/champion_challenger.py`
Se codificó la clase `ChampionChallengerSimulator`, la cual permite:
- **Ejecución en Partición (A/B Split):** Divide dinámicamente un DataFrame de cartera según un parámetro configurable (e.g., 80% Champion / 20% Challenger) y procesa cada subconjunto con su propio motor parametrizado.
- **Ejecución Paralela de Impacto (What-If Analysis):** Evalúa el 100% de los contratos bajo ambas políticas de manera concurrente para generar una matriz comparativa cuenta por cuenta, identificando qué porcentaje exacto de clientes cambiaría de decisión.
- **Generador de KPIs Comparativos:** Calcula automáticamente la tasa de aprobación, contención, cancelación y la variación neta de exposición monetaria (Delta en MXN) para cada grupo.

### 3.2 Refactorización del Núcleo: `rules.py` y `strategy_manager.py`
- Se enriqueció la dataclass `PolicyParameters` incorporando la bandera `habilitar_matriz_dinamica: bool`.
- Se adaptó el evaluador financiero en `DecisionEngine.process_portfolio()` para que soporte tanto el factor fijo como la matriz multidimensional vectorizada en Pandas/NumPy.

### 3.3 Nueva Pestaña en la Plataforma Web: `src/app/dashboard.py` (Tab 5)
Se integró en la interfaz interactiva la pestaña:
**"🥊 Metodología Champion vs Challenger"**, la cual incorpora:
- Selector de escenarios Challenger preconfigurados (*Challenger Conservador*, *Challenger Expansivo*, *Challenger Anti-Mora*).
- Control deslizante interactivo para configurar la distribución porcentual del tráfico A/B.
- Tarjetas de métricas comparativas con deltas dinámicos de incremento y contención.
- Gráfica de barras agrupada con Plotly para comparar las distribuciones relativas de decisión entre Champion y Challenger.

### 3.4 Ampliación de la Suite de Pruebas: `tests/test_rules_engine.py`
Se diseñaron e incorporaron pruebas automatizadas adicionales, elevando la batería a **12 pruebas unitarias**:
- `test_dynamic_matrix_sizing()`: Comprueba que un cliente con score 810 reciba exactamente +35% de cupo y uno con score 730 reciba +15%.
- `test_champion_challenger_simulation()`: Verifica la correcta partición del universo de cuentas y la integridad de los KPIs de cada política.

### 3.5 Rediseño Integral de la Interfaz y Experiencia de Usuario (UI/UX Fintech)
Para elevar la plataforma al nivel visual de un software bancario corporativo, se transformó la capa de presentación:
- **Sistema Tipográfico Fintech:** Adopción de las fuentes *Plus Jakarta Sans* para lectura ejecutiva y *JetBrains Mono* para datos numéricos y de contrato.
- **Tarjetas KPI Personalizadas:** Sustitución de las métricas planas por tarjetas con elevación suave, micro-animaciones en *hover*, contenedores de iconos temáticos y cápsulas de variación porcentual.
- **Navegación Moderna tipo Cápsula:** Rediseño de las pestañas en formato *pill segmented controls* con iluminación y sombras suaves.
- **Velocímetro Gauge FICO (Expediente 360°):** Integración de un tacómetro interactivo en Plotly que mapea la calificación crediticia del cliente entre 300 y 850 puntos con cuatro bandas visuales de riesgo (*Subprime*, *Vulnerable*, *Moderado*, *Prime*).
- **Homogeneización Cromática:** Unificación estricta de la paleta de colores en todas las visualizaciones (Esmeralda, Azul Índigo, Ámbar, Naranja y Carmesí) para facilitar la lectura inmediata a comités evaluadores.

---

## 4. Resultados Experimentales en la Cartera Base (2,500 Cuentas)

Al someter la cartera simulada de 2,500 contratos crediticios al nuevo módulo comparativo (Champion estándar vs. Challenger Conservador con corte de default preventivo a 60 días y score prime a 750), se obtuvieron los siguientes resultados analíticos:

| Dimensión de Análisis | Estrategia Champion (Línea Base) | Estrategia Challenger (Conservadora) | Variación Metodológica |
| :--- | :---: | :---: | :---: |
| **Cuentas Asignadas (80/20)** | 2,000 cuentas (80%) | 500 cuentas (20%) | Partición A/B validada |
| **Tasa de Expansión / Aprobación** | 25.10% | 18.40% | -6.70% (Filtro Prime más estricto) |
| **Tasa de Mantenimiento Regular** | 45.25% | 48.20% | +2.95% (Mayor retención estándar) |
| **Tasa de Reducción Preventiva** | 15.90% | 17.00% | +1.10% (Mitigación temprana) |
| **Tasa de Bloqueo / Contención** | 8.75% | 10.20% | +1.45% (Mayor blindaje preventivo) |
| **Tasa de Cancelación / Cobranza** | 5.00% | 6.20% | +1.20% (Corte oportuno a 60 días) |
| **Delta de Exposición Neta (MXN)** | +$4,120,500.00 MXN | -$1,350,200.00 MXN | Reducción de saldo expuesto al riesgo |

**Conclusión del Experimento:** La metodología Champion/Challenger demuestra que la política Challenger mitiga un 2.65% adicional de riesgo crediticio crítico antes de que la cartera madure a default severo, permitiendo al analista de riesgo respaldar sus propuestas ante comités directivos con evidencia cuantitativa.

---

## 5. Cronograma de Próximos Avances Semanales

Para dar cumplimiento a la planeación periódica de la residencia profesional, se establece el siguiente cronograma de entregables:

```
                                  CRONOGRAMA DE ENTREGABLES
  [SEMANA ACTUAL]        [PRÓXIMA SEMANA]        [SEMANA SIGUIENTE]       [SEMANA DE CIERRE]
 ┌───────────────┐      ┌───────────────┐      ┌──────────────────┐      ┌──────────────────┐
 │ METODOLOGÍA   │ ───> │ SISTEMA DE    │ ───> │ REPORTING        │ ───> │ STRESS TESTING   │
 │ Champion /    │      │ ALERTAS       │      │ REGULATORIO      │      │ MASIVO Y MEMORIA │
 │ Challenger    │      │ TEMPRANAS     │      │ AUDITABLE        │      │ TÉCNICA FINAL    │
 └───────────────┘      └───────────────┘      └──────────────────┘      └──────────────────┘
```

1. **Semana Actual (Completada):**
   - Formalización del marco metodológico de ingeniería y riesgo.
   - Implementación del módulo Champion/Challenger y Matriz Bidimensional de Límites.
   - Despliegue de la Pestaña 5 en Streamlit y batería de pruebas en Pytest (12/12 exitosas).
2. **Próxima Semana (Semana 2 de Avances Metodológicos):**
   - **Módulo de Sistema de Alertas Tempranas (*Early Warning Indicators - EWI*):** Detección heurística de patrones de estrés atípico (aumento súbito de velocidad de gasto en días previos al corte).
3. **Semana 3:**
   - **Motor Automatizado de Reportes Ejecutivos:** Generación y descarga directa desde el dashboard de reportes de auditoría en formato PDF y Excel con tablas cruzadas y gráficos vectoriales embebidos.
4. **Semana 4 (Cierre de Etapa):**
   - **Pruebas de Estrés Masivo (*Stress Testing*):** Evaluación de rendimiento computacional procesando lotes de 50,000 a 100,000 registros sintéticos en memoria, midiendo latencia y consumo de recursos para la memoria técnica final.

---

**Firma del Residente:**  
**Marco Antonio Oroza Ortega**  
División de Informática  
Tecnológico de Estudios Superiores de Ecatepec (TESE)
