# Documentación Técnica y Conceptual del Proyecto
## Prototipo de Motor de Decisiones Comportamentales para Riesgo de Crédito (Arquitectura Inspirada en PowerCurve Strategy Management)

---

**Institución Académica:** Tecnológico de Estudios Superiores de Ecatepec (TESE)  
**División Académica:** División de Informática  
**Modalidad:** Residencia Profesional  
**Fase de Desarrollo:** Fase 1 — Especificación Conceptual, Arquitectura y Reglas de Negocio  
**Autor / Residente:** Marco Antonio Oroza Ortega  
**Versión del Documento:** 1.0.0  
**Fecha:** Septiembre 2026  

---

## 1. Introducción y Justificación del Proyecto

### 1.1 Contexto de la Gestión del Riesgo Crediticio en Banca Minorista
En el ciclo de vida de los productos de crédito revolvente (tarjetas de crédito, líneas de sobregiro y créditos personales), la fase de administración de cartera (*Account Management* o Mantenimiento de Cuentas) representa el periodo donde se materializa la mayor cantidad de pérdidas crediticias no anticipadas. A diferencia de la evaluación inicial (*Origination* o Evaluación de Admisión), donde el análisis se basa en modelos estáticos de prospección y buró crediticio externo, el **análisis comportamental** aprovecha la interacción dinámica continua del acreditado con la entidad financiera.

La predicción de impago y la mitigación de quebrantos financieros dependen de la detección temprana de anomalías operativas: incrementos abruptos en la utilización de la línea de crédito, degradación paulatina de la puntualidad en los días de pago, dependencia de pagos mínimos mensuales y cambios en el *score* comportamental interno.

```
                   Ciclo de Decisión en Account Management
 +-------------------+      +----------------------+      +----------------------+
 | Ingesta Mensual   | ---> | Motor Comportamental | ---> | Acciones Tácticas    |
 | Transaccional/Mora|      | (Políticas + Reglas) |      | Línea, Bloqueo, Cobro|
 +-------------------+      +----------------------+      +----------------------+
```

### 1.2 Planteamiento del Problema: La Brecha entre Herramientas Ofimáticas y Motores Empresariales
Históricamente, diversas áreas de soporte y análisis de riesgo en instituciones de crédito e intermediarios financieros han operado estrategias crediticias mediante hojas de cálculo (Microsoft Excel) y procesos semi-manuales. Este enfoque presenta limitaciones críticas:

1. **Falta de Trazabilidad y Gobernanza:** Las hojas de cálculo no garantizan un registro inmutable de auditoría (*audit trail*) sobre por qué se tomó una decisión específica (e.g., qué regla gatilló el recorte de una línea de crédito), vulnerando estándares regulatorios establecidos por la Comisión Nacional Bancaria y de Valores (CNBV) y los lineamientos de Basilea III/IV.
2. **Fragilidad Operativa y Falta de Determinismo:** El manejo manual de macros y fórmulas expone al sistema a inconsistencias de captura, errores de cálculo, pérdida de versiones y cuellos de botella humanos.
3. **Incapacidad de Escalar a Volúmenes Masivos:** Las carteras minoristas procesan millones de registros al cierre mensual de facturación (*corte contable*). Una solución basada en hojas de cálculo colapsa ante la necesidad de procesar lotes concurrentes en ventanas de tiempo reducidas (*batch processing windows*).
4. **Acoplamiento Inadecuado en el Core Bancario:** En el extremo opuesto, codificar reglas de riesgo directamente en los sistemas centrales transaccionales (*Core Banking Systems*) resulta prohibitivo, pues cualquier cambio de política requiere ciclos extensos de desarrollo, pruebas y despliegues monolíticos.

### 1.3 Justificación y Valor Técnico del Proyecto
Para solventar esta problemática, el mercado financiero implementa motores de decisiones especializados, siendo **Experian PowerCurve Strategy Management** uno de los referentes internacionales más robustos. Estos sistemas desacoplan la **lógica de negocio y política de crédito** del software base, permitiendo parametrizar, simular y ejecutar árboles y matrices de decisión con alto rendimiento y total reproducibilidad.

El presente proyecto de residencia profesional desarrollado por **Marco Antonio Oroza Ortega** tiene por objeto el diseño e implementación de un **Prototipo de Motor de Decisiones Comportamentales**, el cual emula las funciones primarias de diseño estratégico de PowerCurve:
- Estandarización de la ingesta de datos de cartera.
- Ejecución determinística de matrices de riesgo y reglas jerárquicas de corte (*knock-out* y *treatment allocation*).
- Asignación formal de códigos de razón (*Reason Codes*) para explicabilidad algorítmica.
- Generación de un reporte gerencial y analítico accesible para la validación de comités de riesgo.

---

## 2. Alcance del Prototipo ("Mini-PowerCurve")

Para delimitar con precisión la viabilidad técnica y académica del proyecto dentro del periodo de residencias profesionales, se establece formalmente la frontera entre los elementos que formarán parte del desarrollo (*In-Scope*) y las capacidades corporativas de infraestructura que quedarán fuera (*Out-of-Scope*).

```
+-----------------------------------------------------------------------------+
|                            FRONTERA DEL PROYECTO                            |
|                                                                             |
|   [ DENTRO DEL ALCANCE (IN-SCOPE) ]       [ FUERA DEL ALCANCE (OUT-SCOPE) ] |
|                                                                             |
|   * Ingesta por lotes (Batch CSV/JSON)    * Conexión síncrona Core IBM z/OS |
|   * Validación de Calidad de Datos        * Streaming transaccional Kafka   |
|   * Cálculo de deltas comportamentales    * Consultas en vivo Buró Crédito  |
|   * Motor de Reglas en Cascada            * Módulos criptográficos HSM      |
|   * Reason Codes auditables               * Reentrenamiento ML distribuido  |
|   * Dashboard analítico en Streamlit      * Autenticación LDAP/AD bancario  |
+-----------------------------------------------------------------------------+
```

### 2.1 Componentes Dentro del Alcance (*In-Scope*)
1. **Módulo de Ingesta y Validación de Calidad de Datos (*Data Contract & Quality*):**
   - Lectura de archivos estructurados (CSV, JSON, DataFrames) simulando la foto de cierre mensual de la cartera crediticia.
   - Validación sintáctica y semántica de tipos de datos, valores atípicos y nulos.
2. **Capa de Ingeniería de Variables Comportamentales (*Feature Engineering Layer*):**
   - Transformación de variables crudas en indicadores de estrés crediticio (e.g., cálculo del porcentaje de utilización de la línea, pendiente de deterioro de días de atraso en los últimos tres meses, indicador de persistencia de pagos mínimos).
3. **Núcleo del Motor de Reglas (*Decision Engine Core*):**
   - Implementación de un motor modular y parametrizable que evalúe condiciones lógicas compuestas en orden jerárquico de prelación (*Precedence Tree*).
   - Clasificación de clientes en categorías de decisión estandarizadas:
     - `APROBAR_INCREMENTO_LINEA` (Estrategia de crecimiento / Cross-sell).
     - `MANTENER_CONDICIONES` (Comportamiento estable estándar).
     - `REDUCIR_LINEA_PREVENTIVA` (Mitigación de exposición ante señales tempranas).
     - `BLOQUEO_TEMPORAL_LINEA` (Contención ante mora activa o sobreapalancamiento).
     - `CANCELACION_Y_COBRANZA` (Acción de castigo o recuperación inmediata).
4. **Sistema de Auditoría y Códigos de Razón (*Audit Trail & Reason Codes*):**
   - Cada decisión emitida asociará de manera determinística un código identificador unívoco (e.g., `RC_MORA_CONSECUTIVA_CRECIENTE`, `RC_UTILIZACION_CRITICA_SCORE_BAJO`), garantizando el cumplimiento del principio de explicabilidad.
5. **Interfaz de Simulación y Análisis Táctico (*Tactical Dashboard en Streamlit*):**
   - Panel de control interactivo que permita a los analistas de riesgo subir un archivo de cartera, ajustar los umbrales de las políticas (*cut-offs*) y visualizar la matriz de confusión, distribuciones poblacionales y el impacto financiero simulado.

### 2.2 Componentes Fuera del Alcance (*Out-of-Scope*)
1. **Conexión Directa a Infraestructuras Core Transaccionales:**
   - No se implementarán enlaces propietarios mediante colas IBM MQ o protocolos bancarios como ISO 8583 con el mainframe central de la institución.
2. **Consultas en Tiempo Real a Sociedades de Información Crediticia (SIC):**
   - El prototipo no consumirá las APIs síncronas de Buró de Crédito o Círculo de Crédito; los datos externos se asumen precargados como variables sintéticas dentro del dataset de entrada.
3. **Entrenamiento y Optimización de Redes Neuronales o Modelos de Machine Learning en Caliente:**
   - El proyecto no tiene por objeto la creación de un nuevo algoritmo de scoring predictivo, sino la simulación de la **capa de toma de decisiones estratégicas por reglas de negocio** (equivalente al módulo *Strategy Management* de PowerCurve).
4. **Infraestructura de Autenticación Bancaria Multi-Tenant:**
   - No se integrarán mecanismos de seguridad corporativa como Active Directory corporativo, Kerberos o módulos de seguridad de hardware (HSM).

---

## 3. Diccionario de Datos (Variables Comportamentales)

El motor operará sobre una estructura estandarizada de variables a nivel cliente-cuenta, modelada a partir de los atributos comúnmente extraídos durante los procesos de corte de cartera en banca comercial.

| Nombre de la Variable | Tipo de Dato | Formato / Rango | Descripción de Negocio y Riesgo | Justificación en el Motor |
| :--- | :--- | :--- | :--- | :--- |
| `ID_CLIENTE` | Alfanumérico (`str`) | `CLI-[0-9]{8}` | Identificador único del acreditado dentro del sistema bancario. | Llave primaria de auditoría y rastreo de decisiones. |
| `ID_CONTRATO` | Alfanumérico (`str`) | `ACC-[0-9]{10}` | Identificador de la cuenta o tarjeta de crédito evaluada. | Permite diferenciar decisiones si un cliente posee múltiples productos. |
| `LIMITE_CREDITO_ACTUAL` | Numérico Decimal (`float`) | $1,000.00 – $500,000.00 MXN | Línea de crédito total asignada y contractualmente vigente. | Base de cálculo para dimensionar la exposición monetaria y ajustes de cupo. |
| `SALDO_ACTUAL` | Numérico Decimal (`float`) | $\ge 0.00$ MXN | Saldo deudor consolidado a la fecha del corte. | Determina el monto insoluto real expuesto al riesgo de impago. |
| `PORC_USO_LINEA` | Numérico Decimal (`float`) | 0.00% – 150.00% (Ratio $[0.0, 1.5]$) | Ratio de apalancamiento: $\frac{\text{SALDO\_ACTUAL}}{\text{LIMITE\_CREDITO\_ACTUAL}} \times 100$. | Señal primaria de estrés financiero; utilizaciones sostenidas $> 80\%$ preceden al default. |
| `DIAS_ATRASO_M1` | Entero (`int`) | $\ge 0$ días | Días de atraso en el mes inmediato anterior (Mes $t-1$). | Indicador de mora actual y más reciente. Umbral clave para acciones preventivas. |
| `DIAS_ATRASO_M2` | Entero (`int`) | $\ge 0$ días | Días de atraso reportados hace dos meses (Mes $t-2$). | Permite evaluar la tendencia de transición de morosidad (*Roll Rate* de cubos de mora). |
| `DIAS_ATRASO_M3` | Entero (`int`) | $\ge 0$ días | Días de atraso reportados hace tres meses (Mes $t-3$). | Base para detectar morosidad crónica o recurrente a mediano plazo. |
| `PAGOS_MINIMOS_CONSECUTIVOS` | Entero (`int`) | 0 – 12 meses | Número consecutivo de meses en los que el cliente sólo amortizó el pago mínimo. | Indicador de deterioro en la liquidez; alto predictor de insolvencia a largo plazo. |
| `NUM_SOBREGIROS_U6M` | Entero (`int`) | 0 – 6 ocasiones | Frecuencia de incidentes donde el saldo deudor rebasó la línea autorizada en el último semestre. | Señal de falta de control presupuestal o comportamiento riesgoso del acreditado. |
| `SCORE_COMPORTAMENTAL` | Entero (`int`) | 300 – 850 puntos | Calificación estadística interna de propensión de pago (*Behavioral Score*). | Ponderador cuantitativo del riesgo relativo; define la segmentación en matrices de corte. |
| `ANTIGUEDAD_CUENTA_MESES` | Entero (`int`) | $\ge 1$ mes | Tiempo transcurrido desde la firma y activación del contrato crediticio. | Factor de madurez de cartera; los clientes nuevos (< 6 meses) tienen reglas de contención más rígidas. |
| `FLAG_REESTRUCTURA_PREVIA` | Booleano / Entero (`int`) | 0 = No, 1 = Sí | Bandera que indica si el crédito ha atravesado un plan de reestructura o condonación. | Criterio de exclusión automática para aumentos de cupo y políticas preventivas especiales. |

---

## 4. Definición de Reglas de Negocio (El Corazón del Motor)

El motor operará bajo un esquema de **prelación estricta y árboles de decisión jerárquicos**. En la ingeniería de riesgos crediticios, el orden de evaluación es fundamental: las reglas de contención de pérdidas severas (*Knock-out Rules*) se evalúan prioritariamente antes de considerar acciones de expansión comercial o de mantenimiento.

```
                      Jerarquía de Evaluación del Motor
                                      
                         [ Ingesta de Cuenta ]
                                   │
                                   ▼
                ┌─────────────────────────────────────┐
                │ 1. POLÍTICA KNOCK-OUT / SEVERA     │ ──> [ CANCELACIÓN / COBRANZA ]
                │    (Mora >= 90d o Reestructura)    │
                └─────────────────────────────────────┘
                                   │ (Pasa)
                                   ▼
                ┌─────────────────────────────────────┐
                │ 2. POLÍTICA DE CONTENCIÓN URGENTE  │ ──> [ BLOQUEO TEMPORAL ]
                │    (Deterioro Acelerado M1>M2 o Uso)│
                └─────────────────────────────────────┘
                                   │ (Pasa)
                                   ▼
                ┌─────────────────────────────────────┐
                │ 3. POLÍTICA DE MITIGACIÓN PREVENTIVA│ ──> [ REDUCCIÓN DE LÍNEA ]
                │    (Score bajo + Mínimos + Uso alto)│
                └─────────────────────────────────────┘
                                   │ (Pasa)
                                   ▼
                ┌─────────────────────────────────────┐
                │ 4. POLÍTICA DE EXPANSIÓN PROACTIVA  │ ──> [ INCREMENTO DE LÍNEA ]
                │    (Score Excelente + 0 Mora + Uso) │
                └─────────────────────────────────────┘
                                   │ (No califica)
                                   ▼
                         [ MANTENER CONDICIONES ]
```

---

### Regla 1: Política Knock-Out de Riesgo Severo (Cancelación de Línea y Envío a Cobranza)
* **Objetivo de Riesgo:** Cortar la línea de crédito de forma definitiva en cuentas que han traspasado el umbral contable de cartera vencida no amortizable (90 días de mora o *Default* formal según IFRS 9 / Basilea) o que presentan reestructuras previas con mora activa.
* **Lógica de Decisión:**
$$\text{SI } (\text{DIAS\_ATRASO\_M1} \ge 90) \lor (\text{FLAG\_REESTRUCTURA\_PREVIA} = 1 \land \text{DIAS\_ATRASO\_M1} \ge 30)$$
* **Acción Emitida:** `CANCELAR_LINEA_Y_ENVIO_COBRANZA`
* **Parámetros de Salida:**
  - `Nuevo_Limite` = $0.00
  - `Estatus_Tarjeta` = `CANCELADA_POR_RIESGO`
  - `Codigo_Razon` = `RC_DEFAULT_SEVERO_IFRS9`

---

### Regla 2: Política de Contención Inmediata por Deterioro Acelerado (Bloqueo Temporal)
* **Objetivo de Riesgo:** Frenar el sobreendeudamiento transaccional de acreditados cuya morosidad se encuentra en fase activa de crecimiento intermensual (*Roll-forward* negativo de mora) o que combinan sobregiro técnico con retraso en el pago.
* **Lógica de Decisión:**
$$\text{SI } (\text{DIAS\_ATRASO\_M1} \ge 30 \land \text{DIAS\_ATRASO\_M1} > \text{DIAS\_ATRASO\_M2}) \lor (\text{PORC\_USO\_LINEA} \ge 95\% \land \text{DIAS\_ATRASO\_M1} \ge 15)$$
* **Acción Emitida:** `BLOQUEO_TEMPORAL_LINEA`
* **Parámetros de Salida:**
  - `Nuevo_Limite` = $\text{LIMITE\_CREDITO\_ACTUAL}$ (Sin modificación nominal)
  - `Estatus_Tarjeta` = `SUSPENDIDA_TEMPORAL`
  - `Codigo_Razon` = `RC_DETERIORO_MORA_ROLLFORWARD_CRITICO`

---

### Regla 3: Política de Mitigación Preventiva de Exposición (Reducción de Línea de Crédito)
* **Objetivo de Riesgo:** Minimizar el saldo en riesgo (*Exposure at Default* - EAD) en cuentas que, aunque no han caído en mora severa, presentan un perfil de fatiga crediticia persistente (abuso crónico de pagos mínimos, calificación comportamental en rangos bajos y uso intensivo de la línea autorizada).
* **Lógica de Decisión:**
$$\text{SI } (\text{SCORE\_COMPORTAMENTAL} < 580 \land \text{PORC\_USO\_LINEA} \ge 80\%) \lor (\text{PAGOS\_MINIMOS\_CONSECUTIVOS} \ge 4 \land \text{SCORE\_COMPORTAMENTAL} < 620)$$
* **Acción Emitida:** `REDUCIR_LINEA_PREVENTIVA`
* **Parámetros de Salida:**
  - $\text{Nuevo\_Limite} = \max(\text{SALDO\_ACTUAL} \times 1.05, \, \text{LIMITE\_CREDITO\_ACTUAL} \times 0.60)$
  - `Estatus_Tarjeta` = `ACTIVA_REDUCIDA`
  - `Codigo_Razon` = `RC_ESTRES_FINANCIERO_PAGOS_MINIMOS_PERSISTENTES`

---

### Regla 4: Política de Crecimiento Proactivo de Cartera (Incremento de Línea Autorizado)
* **Objetivo de Riesgo:** Maximizar la rentabilidad y la fidelización en cuentas maduras que evidencian solvencia comprobada, disciplina de pago impecable y capacidad holgada de endeudamiento.
* **Lógica de Decisión:**
$$\text{SI } (\text{SCORE\_COMPORTAMENTAL} \ge 720) \land (\text{DIAS\_ATRASO\_M1} = 0 \land \text{DIAS\_ATRASO\_M2} = 0 \land \text{DIAS\_ATRASO\_M3} = 0) \land$$
$$(40\% \le \text{PORC\_USO\_LINEA} \le 75\%) \land (\text{ANTIGUEDAD\_CUENTA\_MESES} \ge 12) \land (\text{NUM\_SOBREGIROS\_U6M} = 0) \land (\text{FLAG\_REESTRUCTURA\_PREVIA} = 0)$$
* **Acción Emitida:** `INCREMENTAR_LINEA_PROACTIVO`
* **Parámetros de Salida:**
  - $\text{Nuevo\_Limite} = \text{LIMITE\_CREDITO\_ACTUAL} \times 1.25$ (+25% de incremento)
  - `Estatus_Tarjeta` = `ACTIVA_PREMIUM`
  - `Codigo_Razon` = `RC_CLIENTE_PRIME_EXCELENTE_HISTORIAL`

---

### Política Residual (Comportamiento por Defecto)
* **Condición:** Si la cuenta no cumple ninguna de las 4 condiciones anteriores.
* **Acción Emitida:** `MANTENER_CONDICIONES_ACTUALES`
* **Parámetros de Salida:**
  - $\text{Nuevo\_Limite} = \text{LIMITE\_CREDITO\_ACTUAL}$
  - `Estatus_Tarjeta` = `ACTIVA_REGULAR`
  - `Codigo_Razon` = `RC_PERFIL_DENTRO_DE_TOLERANCIA_ESTANDAR`

---

## 5. Arquitectura y Propuesta Tecnológica

El desarrollo del software se estructura bajo principios de diseño limpio y arquitectura modular:
1. **Ingesta y Contratos de Datos:** Validación de tipos y calidad de variables con Pydantic.
2. **Ingeniería de Variables Comportamentales:** Cálculo vectorial de deltas, ratios de apalancamiento y métricas de morosidad.
3. **Núcleo del Motor de Decisiones:** Evaluación jerárquica en cascada con generación determinística de códigos de razón.
4. **Persistencia y Auditoría:** Generación de log de auditoría reproducible para comités de riesgo.
5. **Capa de Presentación:** Dashboard interactivo en Streamlit con visualizaciones analíticas en Plotly.
