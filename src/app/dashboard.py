"""
Dashboard Ejecutivo del Motor de Decisiones Comportamentales (Mini-PowerCurve).
Proyecto de Residencia Profesional: Marco Antonio Oroza Ortega - TESE (División de Informática).
"""

import os
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path para resolución de módulos
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.schema.account_schema import validate_portfolio_df
from src.pipeline.feature_engineering import compute_behavioral_features
from src.engine.rules import PolicyParameters, REASON_CODES, DECISION_NAMES
from src.engine.strategy_manager import DecisionEngine
from src.engine.audit import generate_audit_summary
from src.data_generator import generate_synthetic_portfolio



# Configuración de página
st.set_page_config(
    page_title="PowerCurve Behavioral Engine | TESE Informática",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para estética bancaria de alta calidad
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 50%, #003566 100%);
        padding: 1.8rem 2rem;
        border-radius: 14px;
        color: #ffffff;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(0, 53, 102, 0.2);
    }
    
    .badge-tese {
        background: #0077b6;
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-right: 8px;
    }
    
    .badge-collab {
        background: #00b4d8;
        color: #0d1b2a;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
    }
    
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-title {
        color: #64748b;
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.3rem 0;
    }
    .kpi-delta-pos {
        color: #059669;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .kpi-delta-neg {
        color: #dc2626;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .decision-badge-r4 { background-color: #d1fae5; color: #065f46; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .decision-badge-r0 { background-color: #e0f2fe; color: #0369a1; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .decision-badge-r3 { background-color: #fef3c7; color: #92400e; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .decision-badge-r2 { background-color: #ffedd5; color: #9a3412; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
    .decision-badge-r1 { background-color: #fee2e2; color: #991b1b; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Encabezado institucional
st.markdown("""
<div class="main-header">
    <div style="margin-bottom: 0.6rem;">
        <span class="badge-tese">TESE • DIVISIÓN DE INFORMÁTICA</span>
        <span class="badge-collab">MOTOR COMPORTAMENTAL • RIESGO DE CRÉDITO</span>
    </div>
    <h1 style="margin: 0; font-size: 2.1rem; font-weight: 700;">Plataforma de Decisiones Comportamentales</h1>
    <p style="margin: 0.4rem 0 0 0; color: #94a3b8; font-size: 0.95rem;">
        Simulador de Políticas de Riesgo y Mantenimiento de Cartera Crediticia (Arquitectura Tipo Experian PowerCurve)
    </p>
    <div style="margin-top: 0.8rem; padding-top: 0.6rem; border-top: 1px solid rgba(255,255,255,0.15); display: flex; justify-content: space-between; font-size: 0.85rem; color: #cbd5e1;">
        <span>👨‍💻 <strong>Residente / Autor:</strong> Marco Antonio Oroza Ortega</span>
        <span>🏛️ <strong>Tecnológico de Estudios Superiores de Ecatepec (TESE)</strong></span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# BARRA LATERAL: CONTROL DE ESTRATEGIAS
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/bank-building.png", width=56)
    st.subheader("Gestión de Estrategia (Strategy Design)")
    
    st.markdown("### 1. Ingesta de Cartera")
    data_source = st.radio(
        "Fuente de datos:",
        ["Cartera Sintética Precargada (2,500 Cuentas)", "Cargar Archivo CSV Externo", "Regenerar Nueva Cartera Sintética"],
        index=0
    )

    df_raw = None
    if data_source == "Cartera Sintética Precargada (2,500 Cuentas)":
        data_path = os.path.join("data", "raw", "cartera_clientes_simulada.csv")
        if not os.path.exists(data_path):
            df_raw = generate_synthetic_portfolio(2500)
            os.makedirs("data/raw", exist_ok=True)
            df_raw.to_csv(data_path, index=False)
        else:
            df_raw = pd.read_csv(data_path)
            
    elif data_source == "Cargar Archivo CSV Externo":
        uploaded_file = st.file_uploader("Selecciona el archivo CSV de cartera:", type=["csv"])
        if uploaded_file is not None:
            df_raw = pd.read_csv(uploaded_file)
        else:
            st.info("Sube un archivo para comenzar o selecciona la cartera precargada.")
            
    else: # Regenerar
        n_sim = st.slider("Tamaño de muestra a generar:", 500, 10000, 3000, step=500)
        seed_sim = st.number_input("Semilla aleatoria:", min_value=1, value=123)
        if st.button("Generar Nueva Muestra", use_container_width=True):
            df_raw = generate_synthetic_portfolio(n_sim, random_seed=int(seed_sim))
            st.success(f"Generadas {n_sim} cuentas.")

    st.markdown("---")
    st.markdown("### 2. Parametrización de Políticas (Cut-offs)")
    
    with st.expander("Regla 1: Knock-Out Severo", expanded=False):
        p_mora_default = st.slider("Días mora Default (IFRS 9):", 60, 180, 90, 5)
        p_mora_reestructura = st.slider("Días mora en Reestructura:", 15, 60, 30, 5)

    with st.expander("Regla 2: Contención Inmediata", expanded=False):
        p_mora_contencion = st.slider("Días mora para Roll-forward:", 15, 60, 30, 5)
        p_uso_critico = st.slider("% Uso crítico para congelar:", 85.0, 110.0, 95.0, 1.0)
        p_mora_critica = st.slider("Días mora con uso crítico:", 5, 30, 15, 1)

    with st.expander("Regla 3: Mitigación Preventiva", expanded=False):
        p_score_subprime = st.slider("Score Subprime de alerta:", 450, 650, 580, 10)
        p_uso_fatiga = st.slider("% Uso línea para fatiga:", 70.0, 95.0, 80.0, 5.0)
        p_minimos_alerta = st.slider("Pagos mínimos consecutivos:", 2, 8, 4, 1)
        p_factor_reduccion = st.slider("Factor de nueva línea (% del cupo):", 0.40, 0.80, 0.60, 0.05)

    with st.expander("Regla 4: Expansión Proactiva", expanded=False):
        p_score_prime = st.slider("Score Prime mínimo:", 680, 800, 720, 10)
        p_uso_min_exp = st.slider("% Uso mínimo para calificar:", 20.0, 50.0, 40.0, 5.0)
        p_uso_max_exp = st.slider("% Uso máximo para calificar:", 65.0, 90.0, 75.0, 5.0)
        p_factor_incremento = st.slider("Factor incremento de línea:", 1.10, 1.50, 1.25, 0.05)

    # Objeto de parámetros
    policy_params = PolicyParameters(
        dias_mora_default=p_mora_default,
        dias_mora_reestructura=p_mora_reestructura,
        dias_mora_contencion=p_mora_contencion,
        uso_linea_critico=p_uso_critico,
        dias_mora_sobregiro=p_mora_critica,
        score_subprime=p_score_subprime,
        uso_linea_fatiga=p_uso_fatiga,
        minimos_consecutivos_alerta=p_minimos_alerta,
        factor_reduccion_linea=p_factor_reduccion,
        score_prime=p_score_prime,
        uso_min_expansion=p_uso_min_exp,
        uso_max_expansion=p_uso_max_exp,
        factor_incremento_linea=p_factor_incremento
    )

    st.markdown("---")
    btn_ejecutar = st.button("🚀 Ejecutar Motor de Decisiones", type="primary", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; font-size: 0.82rem; color: #334155;">
        <div style="font-weight: 700; color: #0f172a; font-size: 0.9rem;">Marco Antonio Oroza Ortega</div>
        <div style="color: #475569; margin-top: 2px;">Proyecto de Residencia Profesional</div>
        <div style="color: #0284c7; font-weight: 600; font-size: 0.78rem;">División de Informática • TESE</div>
        <div style="color: #64748b; font-size: 0.75rem;">Simulación de Motor de Riesgo</div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# LÓGICA DE PROCESAMIENTO
# ==========================================
if df_raw is not None:
    # 1. Validación de esquema
    df_clean, validation_warnings = validate_portfolio_df(df_raw)
    
    # 2. Pipeline de variables comportamentales
    df_features = compute_behavioral_features(df_clean)
    
    # 3. Ejecución del motor
    engine = DecisionEngine(policy_params)
    df_decisions = engine.process_portfolio(df_features)
    
    # 4. Auditoría consolidada
    audit_summary = generate_audit_summary(df_decisions)
    
    # Tabs principales
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Resumen Ejecutivo y KPIs",
        "⚙️ Matriz de Transición & Riesgo",
        "🔍 Auditoría 360° de Cuentas",
        "📁 Tabla de Decisiones & Exportación"
    ])

    # ----------------------------------------------------
    # TAB 1: RESUMEN EJECUTIVO Y KPIS
    # ----------------------------------------------------
    with tab1:
        st.subheader("Métricas de Impacto en Cartera Crediticia")
        
        # Tarjetas KPI
        col1, col2, col3, col4 = st.columns(4)
        
        total_cuentas = audit_summary["total_cuentas_procesadas"]
        limite_previo = audit_summary["metricas_financieras"]["limite_vigente_total_mxn"]
        nuevo_limite = audit_summary["metricas_financieras"]["nuevo_limite_total_mxn"]
        delta_neto = audit_summary["metricas_financieras"]["delta_exposicion_neta_mxn"]
        pct_delta = audit_summary["metricas_financieras"]["porcentaje_variacion_linea"]
        
        with col1:
            st.metric("Total Cuentas Evaluadas", f"{total_cuentas:,}")
        with col2:
            st.metric("Límite Vigente Previo", f"${limite_previo:,.2f} MXN")
        with col3:
            st.metric("Nuevo Límite Autorizado", f"${nuevo_limite:,.2f} MXN")
        with col4:
            delta_label = f"{pct_delta:+.2f}%"
            st.metric("Variación Neta de Exposición", f"${delta_neto:+,.2f} MXN", delta=delta_label)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Gráficas ejecutivas
        chart_col1, chart_col2 = st.columns([1, 1])
        
        with chart_col1:
            st.markdown("#### Distribución de Decisiones Tácticas")
            df_dist = df_decisions["DECISION_FINAL"].value_counts().reset_index()
            df_dist.columns = ["Decisión", "Cuentas"]
            
            # Paleta de colores estandarizada
            color_map = {
                "INCREMENTAR_LINEA_PROACTIVO": "#10b981",
                "MANTENER_CONDICIONES_ACTUALES": "#3b82f6",
                "REDUCIR_LINEA_PREVENTIVA": "#f59e0b",
                "BLOQUEO_TEMPORAL_LINEA": "#f97316",
                "CANCELAR_LINEA_Y_ENVIO_COBRANZA": "#ef4444"
            }
            
            fig_pie = px.pie(
                df_dist,
                names="Decisión",
                values="Cuentas",
                color="Decisión",
                color_discrete_map=color_map,
                hole=0.45
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=340, showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown("#### Impacto Monetario Neto por Decisión (MXN)")
            df_impact = df_decisions.groupby("DECISION_FINAL")["DELTA_EXPOSICION"].sum().reset_index()
            df_impact.columns = ["Decisión", "Delta_MXN"]
            
            fig_bar = px.bar(
                df_impact,
                x="Decisión",
                y="Delta_MXN",
                color="Decisión",
                color_discrete_map=color_map,
                text_auto='.2s'
            )
            fig_bar.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=340,
                xaxis_title="",
                yaxis_title="Variación Neta (MXN)",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Segmentación Multidimensional: Score Comportamental vs Utilización de Línea")
        
        # Muestra de puntos para optimizar render interactivo si el dataset es grande
        sample_size = min(1500, len(df_decisions))
        df_scatter = df_decisions.sample(sample_size, random_state=42)
        
        fig_scatter = px.scatter(
            df_scatter,
            x="SCORE_COMPORTAMENTAL",
            y="PORC_USO_LINEA",
            color="DECISION_FINAL",
            color_discrete_map=color_map,
            hover_data=["ID_CLIENTE", "DIAS_ATRASO_M1", "LIMITE_CREDITO_ACTUAL", "NUEVO_LIMITE_CREDITO", "CODIGO_RAZON"],
            labels={"SCORE_COMPORTAMENTAL": "Score Comportamental Interno", "PORC_USO_LINEA": "% Utilización de Línea"},
            opacity=0.75
        )
        fig_scatter.add_hline(y=100.0, line_dash="dash", line_color="red", annotation_text="Límite Máximo de Línea (100%)")
        fig_scatter.update_layout(height=450, margin=dict(t=20, b=20, l=20, r=20), legend_title_text="Decisión Asignada")
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ----------------------------------------------------
    # TAB 2: MATRIZ DE TRANSICIÓN Y RIESGO
    # ----------------------------------------------------
    with tab2:
        st.subheader("Análisis Dinámico de Cartera y Roll Rates")
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown("#### Distribución de Estatus Operativo de la Tarjeta")
            df_estatus = df_decisions["ESTATUS_RESULTANTE"].value_counts().reset_index()
            df_estatus.columns = ["Estatus", "Cuentas"]
            fig_estatus = px.bar(
                df_estatus,
                x="Cuentas",
                y="Estatus",
                orientation="h",
                color="Estatus",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_estatus.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_estatus, use_container_width=True)

        with col_t2:
            st.markdown("#### Explicabilidad: Distribución de Reason Codes")
            df_rc = df_decisions["CODIGO_RAZON"].value_counts().reset_index()
            df_rc.columns = ["Código de Razón", "Ocurrencias"]
            fig_rc = px.bar(
                df_rc,
                x="Ocurrencias",
                y="Código de Razón",
                orientation="h",
                color="Código de Razón",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            fig_rc.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
            st.plotly_chart(fig_rc, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Matriz de Transición de Morosidad (Mes t-2 vs Mes t-1)")
        
        # Categorizar cubos de mora
        def get_bucket(days):
            if days == 0: return "Cero Mora"
            elif days <= 30: return "1-30 Días"
            elif days <= 60: return "31-60 Días"
            elif days <= 90: return "61-90 Días"
            else: return ">90 Días (Default)"
            
        df_decisions["BUCKET_M2"] = df_decisions["DIAS_ATRASO_M2"].apply(get_bucket)
        df_decisions["BUCKET_M1"] = df_decisions["DIAS_ATRASO_M1"].apply(get_bucket)
        
        order = ["Cero Mora", "1-30 Días", "31-60 Días", "61-90 Días", ">90 Días (Default)"]
        cross_tab = pd.crosstab(df_decisions["BUCKET_M2"], df_decisions["BUCKET_M1"]).reindex(index=order, columns=order, fill_value=0)
        
        fig_heat = px.imshow(
            cross_tab,
            text_auto=True,
            labels=dict(x="Morosidad Mes Actual (M1)", y="Morosidad Mes Anterior (M2)", color="Cuentas"),
            color_continuous_scale="Blues"
        )
        fig_heat.update_layout(height=380, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_heat, use_container_width=True)

    # ----------------------------------------------------
    # TAB 3: AUDITORÍA 360° DE CUENTAS (CASE REVIEW)
    # ----------------------------------------------------
    with tab3:
        st.subheader("Inspección Detallada de Cuenta Individual")
        
        cuenta_ids = df_decisions["ID_CLIENTE"].tolist()
        col_sel1, col_sel2 = st.columns([2, 1])
        with col_sel1:
            selected_client = st.selectbox("Seleccione el ID de Cliente a auditar:", cuenta_ids, index=0)
            
        row = df_decisions[df_decisions["ID_CLIENTE"] == selected_client].iloc[0]
        
        # Resumen de Decisión para la cuenta seleccionada
        col_c1, col_c2, col_c3, col_c4 = st.columns(4)
        with col_c1:
            st.markdown(f"**Decisión Final:**  \n`{row['DECISION_FINAL']}`")
        with col_c2:
            st.markdown(f"**Regla Detonada:**  \n`{row['REGLA_DISPARADA']}`")
        with col_c3:
            st.markdown(f"**Código de Razón:**  \n`{row['CODIGO_RAZON']}`")
        with col_c4:
            st.markdown(f"**Estatus de Tarjeta:**  \n`{row['ESTATUS_RESULTANTE']}`")

        st.markdown("---")
        
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.markdown("#### Datos de Línea y Financieros")
            st.write(f"- **Contrato:** `{row['ID_CONTRATO']}`")
            st.write(f"- **Línea Previa:** `${row['LIMITE_CREDITO_ACTUAL']:,.2f} MXN`")
            st.write(f"- **Saldo Actual Insoluto:** `${row['SALDO_ACTUAL']:,.2f} MXN`")
            st.write(f"- **Porcentaje de Uso:** `{row['PORC_USO_LINEA']:.2f}%`")
            st.write(f"- **Nuevo Límite Autorizado:** `${row['NUEVO_LIMITE_CREDITO']:,.2f} MXN`")
            st.write(f"- **Delta de Exposición:** `${row['DELTA_EXPOSICION']:+,.2f} MXN`")

        with col_info2:
            st.markdown("#### Vector de Comportamiento Crediticio")
            st.write(f"- **Score Comportamental:** `{int(row['SCORE_COMPORTAMENTAL'])} pts` ({row['SEGMENTO_SCORE']})")
            st.write(f"- **Días de Atraso M1 (Último mes):** `{int(row['DIAS_ATRASO_M1'])} días`")
            st.write(f"- **Días de Atraso M2 (Hace 2 meses):** `{int(row['DIAS_ATRASO_M2'])} días`")
            st.write(f"- **Días de Atraso M3 (Hace 3 meses):** `{int(row['DIAS_ATRASO_M3'])} días`")
            st.write(f"- **Pagos Mínimos Consecutivos:** `{int(row['PAGOS_MINIMOS_CONSECUTIVOS'])}`")
            st.write(f"- **Sobregiros últimos 6 meses:** `{int(row['NUM_SOBREGIROS_U6M'])}`")
            st.write(f"- **Antigüedad del Contrato:** `{int(row['ANTIGUEDAD_CUENTA_MESES'])} meses`")
            st.write(f"- **Reestructura Previa Activa:** `{'SÍ' if row['FLAG_REESTRUCTURA_PREVIA'] == 1 else 'NO'}`")

        # Explicabilidad didáctica para el evaluador
        st.info(f"💡 **Justificación Técnica de la Decisión:** El acreditado `{row['ID_CLIENTE']}` fue evaluado bajo el árbol de prelación jerárquica. La primera política satisfecha fue `{row['REGLA_DISPARADA']}`, asignándole la acción `{row['DECISION_FINAL']}` y emitiendo el código de razón `{row['CODIGO_RAZON']}`.")

    # ----------------------------------------------------
    # TAB 4: EXPORTACIÓN Y LOG DE AUDITORÍA
    # ----------------------------------------------------
    with tab4:
        st.subheader("Registro de Auditoría y Exportación de Datos")
        
        # Filtro interactivo de la tabla
        filtro_decision = st.multiselect(
            "Filtrar por Decisión:",
            options=df_decisions["DECISION_FINAL"].unique(),
            default=df_decisions["DECISION_FINAL"].unique()
        )
        
        df_filtered = df_decisions[df_decisions["DECISION_FINAL"].isin(filtro_decision)]
        
        cols_display = [
            "ID_CLIENTE", "SCORE_COMPORTAMENTAL", "LIMITE_CREDITO_ACTUAL", "SALDO_ACTUAL",
            "PORC_USO_LINEA", "DIAS_ATRASO_M1", "PAGOS_MINIMOS_CONSECUTIVOS",
            "REGLA_DISPARADA", "DECISION_FINAL", "NUEVO_LIMITE_CREDITO", "DELTA_EXPOSICION", "CODIGO_RAZON"
        ]
        st.dataframe(df_filtered[cols_display], use_container_width=True, height=350)
        
        col_down1, col_down2 = st.columns(2)
        with col_down1:
            csv_data = df_decisions.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Cartera Decidida (CSV)",
                data=csv_data,
                file_name="cartera_decisiones_powercurve.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        with col_down2:
            audit_json = json.dumps(audit_summary, indent=4).encode('utf-8')
            st.download_button(
                label="📜 Descargar Reporte de Auditoría (JSON)",
                data=audit_json,
                file_name=f"audit_trail_{audit_summary['execution_id'][:8]}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    st.warning("No se ha cargado ninguna cartera crediticia. Seleccione una fuente en la barra lateral.")
