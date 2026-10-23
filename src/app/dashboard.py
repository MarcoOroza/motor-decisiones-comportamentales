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
from src.engine.champion_challenger import ChampionChallengerSimulator
from src.engine.early_warning import EarlyWarningSystem, EWI_CATALOG
from src.data_generator import generate_synthetic_portfolio


# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="PowerCurve Behavioral Engine | TESE Informática",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# SISTEMA DE DISEÑO Y ESTILOS CSS FINTECH DE ALTA FIDELIDAD
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
    }

    /* Ocultar barra superior genérica de Streamlit para look corporativo */
    header[data-testid="stHeader"] {
        background: transparent;
    }
    
    /* ENCABEZADO PRINCIPAL FINTECH */
    .main-header {
        background: radial-gradient(circle at 10% 20%, #0f172a 0%, #1e293b 90%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2.2rem 2.4rem;
        border-radius: 20px;
        color: #ffffff;
        margin-bottom: 2rem;
        box-shadow: 0 20px 35px -10px rgba(15, 23, 42, 0.4), 0 0 25px rgba(56, 189, 248, 0.08);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: "";
        position: absolute;
        top: -50%;
        right: -20%;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    /* BADGES INSTITUCIONALES */
    .badge-tese {
        background: rgba(14, 165, 233, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 5px 12px;
        border-radius: 30px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        display: inline-block;
        margin-right: 8px;
        backdrop-filter: blur(4px);
    }
    .badge-collab {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 5px 12px;
        border-radius: 30px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        display: inline-block;
        backdrop-filter: blur(4px);
    }
    
    /* TARJETAS KPI FINTECH MODERNAS */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.2rem;
        margin-bottom: 2rem;
    }
    .kpi-card-lux {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }
    .kpi-card-lux:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px -4px rgba(15, 23, 42, 0.1);
        border-color: #cbd5e1;
    }
    .kpi-icon-wrapper {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        margin-bottom: 0.9rem;
    }
    .kpi-label {
        color: #64748b;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .kpi-big-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0.2rem 0;
        letter-spacing: -0.5px;
    }
    .kpi-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 8px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
    }
    .kpi-pill-pos {
        background: #ecfdf5;
        color: #059669;
        border: 1px solid #a7f3d0;
    }
    .kpi-pill-neg {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    .kpi-pill-neutral {
        background: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }

    /* PESTAÑAS (TABS) MODERNIZADAS TIPO SEGMENTED CONTROL */
    div[data-testid="stTabs"] {
        margin-top: 0.5rem;
    }
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f1f5f9;
        padding: 6px;
        border-radius: 14px;
        border: 1px solid #e2e8f0;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 10px;
        padding: 9px 18px;
        font-weight: 600;
        font-size: 0.88rem;
        color: #64748b;
        background-color: transparent;
        border: none;
        transition: all 0.2s ease;
    }
    div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: #0f172a;
        background-color: rgba(255, 255, 255, 0.6);
    }
    div[data-testid="stTabs"] [aria-selected="true"] {
        background: #0f172a !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.2);
    }
    
    /* BADGES DE DECISIONES CREDITICIAS */
    .badge-decision {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.76rem;
        letter-spacing: 0.3px;
    }
    .dec-r4 { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
    .dec-r0 { background: #e0f2fe; color: #0369a1; border: 1px solid #7dd3fc; }
    .dec-r3 { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
    .dec-r2 { background: #ffedd5; color: #9a3412; border: 1px solid #fdba74; }
    .dec-r1 { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

    /* BADGES DE ALERTAS TEMPRANAS (EWS) */
    .badge-ews {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.76rem;
        letter-spacing: 0.3px;
    }
    .ews-rojo { background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }
    .ews-naranja { background: #ffedd5; color: #9a3412; border: 1px solid #fb923c; }
    .ews-amarillo { background: #fef9c3; color: #854d0e; border: 1px solid #facc15; }
    .ews-verde { background: #dcfce7; color: #166534; border: 1px solid #4ade80; }

    /* CARD DE AUDITORÍA Y PERFIL */
    .dossier-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04);
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# ENCABEZADO INSTITUCIONAL
# -----------------------------------------------------------------------------
st.markdown("""
<div class="main-header">
    <div style="margin-bottom: 0.8rem;">
        <span class="badge-tese">TECNOLÓGICO DE ESTUDIOS SUPERIORES DE ECATEPEC</span>
        <span class="badge-collab">DIVISIÓN DE INFORMÁTICA • RESIDENCIA PROFESIONAL</span>
    </div>
    <h1 style="margin: 0; font-size: 2.3rem; font-weight: 800; letter-spacing: -0.6px; line-height: 1.2;">
        Motor de Decisiones Comportamentales
    </h1>
    <p style="margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 1.05rem; font-weight: 400; max-width: 850px;">
        Plataforma analítica para administración estratégica de cartera crediticia, evaluación multicriterio y experimentación Champion/Challenger (Arquitectura basada en Experian PowerCurve).
    </p>
    <div style="margin-top: 1.4rem; padding-top: 0.9rem; border-top: 1px solid rgba(255,255,255,0.12); display: flex; justify-content: space-between; align-items: center; font-size: 0.88rem; color: #cbd5e1;">
        <div>👨‍💻 <strong>Autor / Residente:</strong> Marco Antonio Oroza Ortega &nbsp;•&nbsp; <strong>Carrera:</strong> Informática</div>
        <div>🏛️ <strong>TESE</strong> &nbsp;•&nbsp; Versión Funcional Fase 2</div>
    </div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# BARRA LATERAL: CONTROL DE ESTRATEGIAS Y PARÁMETROS
# =============================================================================
with st.sidebar:
    st.markdown("### ⚙️ Centro de Estrategia")
    st.caption("Configuración paramétrica del motor tipo PowerCurve")
    
    st.markdown("#### 1. Ingesta de Cartera")
    data_source = st.radio(
        "Origen de datos:",
        ["Cartera Sintética Precargada (2,500 Cuentas)", "Cargar Archivo CSV Externo", "Regenerar Nueva Cartera"],
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
        uploaded_file = st.file_uploader("Subir dataset estructurado (.csv):", type=["csv"])
        if uploaded_file is not None:
            df_raw = pd.read_csv(uploaded_file)
        else:
            st.info("Sube un archivo para procesar o selecciona la cartera precargada.")
            
    else: # Regenerar
        n_sim = st.slider("Tamaño de muestra sintética:", 500, 10000, 2500, step=500)
        seed_sim = st.number_input("Semilla pseudoaleatoria:", min_value=1, value=42)
        if st.button("Generar Nueva Población", use_container_width=True):
            df_raw = generate_synthetic_portfolio(n_sim, random_seed=int(seed_sim))
            st.success(f"Generadas {n_sim} cuentas.")

    st.markdown("---")
    st.markdown("#### 2. Umbrales de Políticas (Cut-offs)")
    
    with st.expander("🛡️ Regla 1: Knock-Out Severo", expanded=False):
        p_mora_default = st.slider("Días mora Default (IFRS 9 / Basilea):", 60, 180, 90, 5)
        p_mora_reestructura = st.slider("Días mora con Reestructura:", 15, 60, 30, 5)

    with st.expander("⚠️ Regla 2: Contención Inmediata", expanded=False):
        p_mora_contencion = st.slider("Días mora para Roll-forward:", 15, 60, 30, 5)
        p_uso_critico = st.slider("% Uso crítico para congelar:", 85.0, 110.0, 95.0, 1.0)
        p_mora_critica = st.slider("Días mora con uso crítico:", 5, 30, 15, 1)

    with st.expander("📉 Regla 3: Mitigación Preventiva", expanded=False):
        p_score_subprime = st.slider("Score Subprime de alerta:", 450, 650, 580, 10)
        p_uso_fatiga = st.slider("% Uso línea para fatiga:", 70.0, 95.0, 80.0, 5.0)
        p_minimos_alerta = st.slider("Pagos mínimos consecutivos:", 2, 8, 4, 1)
        p_factor_reduccion = st.slider("Factor de nueva línea (% del cupo):", 0.40, 0.80, 0.60, 0.05)

    with st.expander("🚀 Regla 4: Expansión Proactiva", expanded=False):
        p_score_prime = st.slider("Score Prime mínimo:", 680, 800, 720, 10)
        p_uso_min_exp = st.slider("% Uso mínimo requerido:", 20.0, 50.0, 40.0, 5.0)
        p_uso_max_exp = st.slider("% Uso máximo admisible:", 65.0, 90.0, 75.0, 5.0)
        p_factor_incremento = st.slider("Factor base de incremento:", 1.10, 1.50, 1.25, 0.05)

    with st.expander("📐 Metodología: Matriz Dinámica", expanded=True):
        p_matriz_dinamica = st.toggle(
            "Activar Matriz por Deciles",
            value=True,
            help="Aplica incrementos (+35%, +25%, +15%) y reducciones (-50%, -35%) escalonadas según deciles de Score"
        )

    with st.expander("🚨 Sistema de Alertas Tempranas (EWS)", expanded=False):
        p_ews_uso = st.slider("Umbral EWS Uso Crítico (%):", 70.0, 95.0, 85.0, 5.0)
        p_ews_minimos = st.slider("Umbral EWS Pagos Mínimos:", 1, 5, 2, 1)

    # Construcción de parámetros
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
    policy_params.habilitar_matriz_dinamica = p_matriz_dinamica

    st.markdown("---")
    st.markdown("""
    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px; font-size: 0.82rem; color: #334155;">
        <div style="font-weight: 700; color: #0f172a; font-size: 0.92rem;">Marco Antonio Oroza Ortega</div>
        <div style="color: #475569; margin: 2px 0;">Proyecto de Residencia Profesional</div>
        <div style="color: #0284c7; font-weight: 600; font-size: 0.79rem;">División de Informática • TESE</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📝 Bitácora Semanal (Changelog)", expanded=False):
        st.markdown("""
        **v2.0.0 (Semana 2 — Actual)**
        - 🚨 **Sistema de Alertas Tempranas (EWS):** 4 Indicadores heurísticos (EWIs) de apalancamiento, pagos mínimos, mora incipiente y sobregiros.
        - 🛡️ **Clasificación IFRS 9 Stage 2:** Semáforos preventivos (Verde, Amarillo, Naranja, Rojo).
        - 🎯 **Matriz de Anticipación:** Cruce de semáforo EWS vs. decisión reactiva.
        - 🧪 **15 Pruebas Unitarias Pytest (100% pass).**
        
        *Racional:* Interceptar indicios sutiles de asfixia financiera con 30-60 días de ventaja antes de que el crédito madure a default severo.
        
        ---
        **v1.5.0 (Semana 1)**
        - 🥊 **Champion / Challenger:** A/B Testing estocástico y simulación *What-If*.
        - 📐 **Matriz Bidimensional:** Incrementos (+15% a +35%) y reducciones escalonadas por deciles FICO, protegiendo el 105% del saldo insoluto.
        - 🏎️ **Velocímetro Gauge FICO:** 4 bandas de riesgo crediticio.
        - 🎨 **Rediseño UI/UX Fintech:** Tipografía corporativa y elevación suave.
        
        *Racional:* Evitar despliegues al 100% a ciegas que causen pérdidas millonarias o rechazos de clientes rentables.
        
        ---
        **v1.0.0 (Línea Base Inicial)**
        - 🏛️ **Arquitectura Limpia:** Contratos Pydantic, pipeline comportamental y árbol de prelación.
        - 🛡️ **4 Reglas Maestras:** Knock-out, Contención, Mitigación y Expansión.
        - 📜 **Auditoría:** Códigos de Razón y logs inmutables.
        
        *Racional:* Sustituir procesos vulnerables en hojas de cálculo por un motor auditable.
        """)


# =============================================================================
# MOTOR DE PROCESAMIENTO
# =============================================================================
if df_raw is not None:
    # 1. Validación de esquema Pydantic
    df_clean, validation_warnings = validate_portfolio_df(df_raw)
    
    # 2. Pipeline vectorial de variables comportamentales
    df_features = compute_behavioral_features(df_clean)
    
    # 3. Orquestador de prelación jerárquica
    engine = DecisionEngine(policy_params)
    df_decisions = engine.process_portfolio(df_features)

    # 4. Sistema de Alertas Tempranas (EWS)
    ews = EarlyWarningSystem(umbral_uso=p_ews_uso, min_pagos_minimos=p_ews_minimos)
    df_decisions = ews.evaluate_portfolio(df_decisions)
    ews_summary = ews.generate_ews_summary(df_decisions)
    
    # 5. Auditoría y métricas consolidadas
    audit_summary = generate_audit_summary(df_decisions)
    
    # -------------------------------------------------------------------------
    # TABS PRINCIPALES CON EXPERIMENTACIÓN METODOLÓGICA
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Resumen Ejecutivo y KPIs",
        "⚙️ Matriz de Transición & Riesgo",
        "🚨 Alertas Tempranas (EWS)",
        "🔍 Expediente y Auditoría 360°",
        "📁 Cartera Decidida & Logs",
        "🥊 Metodología Champion vs Challenger"
    ])

    # Paleta de colores institucional fintech
    color_map = {
        "INCREMENTAR_LINEA_PROACTIVO": "#10b981",    # Emerald
        "MANTENER_CONDICIONES_ACTUALES": "#3b82f6",  # Indigo
        "REDUCIR_LINEA_PREVENTIVA": "#f59e0b",       # Amber
        "BLOQUEO_TEMPORAL_LINEA": "#f97316",         # Orange
        "CANCELAR_LINEA_Y_ENVIO_COBRANZA": "#ef4444" # Rose
    }

    # -------------------------------------------------------------------------
    # TAB 1: RESUMEN EJECUTIVO Y KPIS FINANCIEROS
    # -------------------------------------------------------------------------
    with tab1:
        total_cuentas = audit_summary["total_cuentas_procesadas"]
        limite_previo = audit_summary["metricas_financieras"]["limite_vigente_total_mxn"]
        nuevo_limite = audit_summary["metricas_financieras"]["nuevo_limite_total_mxn"]
        delta_neto = audit_summary["metricas_financieras"]["delta_exposicion_neta_mxn"]
        pct_delta = audit_summary["metricas_financieras"]["porcentaje_variacion_linea"]

        # Tarjetas KPI Estilizadas en HTML
        pill_class = "kpi-pill-pos" if delta_neto >= 0 else "kpi-pill-neg"
        pill_arrow = "▲" if delta_neto >= 0 else "▼"

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card-lux">
                <div class="kpi-icon-wrapper" style="background: #e0f2fe; color: #0284c7;">👥</div>
                <div class="kpi-label">Cartera Evaluada</div>
                <div class="kpi-big-value">{total_cuentas:,}</div>
                <div class="kpi-pill kpi-pill-neutral">100% de contratos auditados</div>
            </div>
            <div class="kpi-card-lux">
                <div class="kpi-icon-wrapper" style="background: #f1f5f9; color: #475569;">💳</div>
                <div class="kpi-label">Límite Vigente Previo</div>
                <div class="kpi-big-value">${limite_previo:,.0f} <span style="font-size:0.9rem;font-weight:500;color:#64748b;">MXN</span></div>
                <div class="kpi-pill kpi-pill-neutral">Exposición contractual base</div>
            </div>
            <div class="kpi-card-lux">
                <div class="kpi-icon-wrapper" style="background: #ede9fe; color: #7c3aed;">🏦</div>
                <div class="kpi-label">Nuevo Límite Autorizado</div>
                <div class="kpi-big-value">${nuevo_limite:,.0f} <span style="font-size:0.9rem;font-weight:500;color:#64748b;">MXN</span></div>
                <div class="kpi-pill kpi-pill-neutral">Asignación tras políticas</div>
            </div>
            <div class="kpi-card-lux">
                <div class="kpi-icon-wrapper" style="background: {'#ecfdf5' if delta_neto >= 0 else '#fef2f2'}; color: {'#059669' if delta_neto >= 0 else '#dc2626'};">
                    {'📈' if delta_neto >= 0 else '📉'}
                </div>
                <div class="kpi-label">Variación Neta de Exposición</div>
                <div class="kpi-big-value" style="color: {'#059669' if delta_neto >= 0 else '#dc2626'};">
                    ${delta_neto:+,.0f} <span style="font-size:0.9rem;font-weight:500;">MXN</span>
                </div>
                <div class="kpi-pill {pill_class}">{pill_arrow} {pct_delta:+.2f}% de variación</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        chart_col1, chart_col2 = st.columns([1, 1])
        
        with chart_col1:
            st.markdown("#### 🍩 Distribución de Decisiones Tácticas")
            df_dist = df_decisions["DECISION_FINAL"].value_counts().reset_index()
            df_dist.columns = ["Decisión", "Cuentas"]
            
            fig_pie = px.pie(
                df_dist,
                names="Decisión",
                values="Cuentas",
                color="Decisión",
                color_discrete_map=color_map,
                hole=0.55
            )
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#ffffff', width=2))
            )
            fig_pie.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=350,
                font=dict(family='Plus Jakarta Sans', size=12),
                showlegend=False
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with chart_col2:
            st.markdown("#### 📊 Impacto Financiero Neto por Segmento (MXN)")
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
                height=350,
                xaxis_title="",
                yaxis_title="Variación Neta (MXN)",
                font=dict(family='Plus Jakarta Sans', size=11),
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🎯 Mapa de Dispersión Estratégico: Score vs Utilización de Línea")
        
        sample_size = min(1500, len(df_decisions))
        df_scatter = df_decisions.sample(sample_size, random_state=42)
        
        fig_scatter = px.scatter(
            df_scatter,
            x="SCORE_COMPORTAMENTAL",
            y="PORC_USO_LINEA",
            color="DECISION_FINAL",
            color_discrete_map=color_map,
            hover_data=["ID_CLIENTE", "DIAS_ATRASO_M1", "LIMITE_CREDITO_ACTUAL", "NUEVO_LIMITE_CREDITO", "CODIGO_RAZON"],
            labels={"SCORE_COMPORTAMENTAL": "Score Comportamental Interno (FICO)", "PORC_USO_LINEA": "% Utilización de Línea"},
            opacity=0.75
        )
        fig_scatter.add_hline(y=100.0, line_dash="dash", line_color="#ef4444", annotation_text="Límite Máximo (100%)", annotation_position="top right")
        fig_scatter.update_layout(
            height=460,
            margin=dict(t=20, b=20, l=20, r=20),
            font=dict(family='Plus Jakarta Sans', size=11),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 2: MATRIZ DE TRANSICIÓN Y ROLL RATES
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("Dinámica Intermensual de Morosidad (Roll Rates)")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### Estatus Operativo Resultante de la Cuenta")
            df_estatus = df_decisions["ESTATUS_RESULTANTE"].value_counts().reset_index()
            df_estatus.columns = ["Estatus", "Cuentas"]
            fig_estatus = px.bar(
                df_estatus,
                x="Cuentas",
                y="Estatus",
                orientation="h",
                color="Estatus",
                color_discrete_sequence=["#10b981", "#3b82f6", "#f59e0b", "#f97316", "#ef4444"]
            )
            fig_estatus.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), font=dict(family='Plus Jakarta Sans'), showlegend=False)
            st.plotly_chart(fig_estatus, use_container_width=True)

        with col_t2:
            st.markdown("#### Explicabilidad Algorítmica: Códigos de Razón (Reason Codes)")
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
            fig_rc.update_layout(height=320, margin=dict(t=10, b=10, l=10, r=10), font=dict(family='Plus Jakarta Sans'), showlegend=False)
            st.plotly_chart(fig_rc, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Matriz de Transición de Mora (Mes t-2 ➔ Mes t-1)")
        
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
        fig_heat.update_layout(height=390, margin=dict(t=20, b=20, l=20, r=20), font=dict(family='Plus Jakarta Sans'))
        st.plotly_chart(fig_heat, use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: SISTEMA DE ALERTAS TEMPRANAS (EARLY WARNING SYSTEM - EWS)
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("🚨 Sistema de Alertas Tempranas (Early Warning System - EWS)")
        st.markdown("""
        El **Sistema de Alertas Tempranas (EWS)** es el estándar de la industria bancaria para detectar indicios de estrés financiero **antes** de que los clientes maduren a mora severa o default (alineado a los requerimientos de la norma **IFRS 9 / Basilea III** para etapas de deterioro *Stage 2*).
        """)

        # 4 KPI Cards de los Semáforos EWS
        total_eval = len(df_decisions)
        n_rojo = int((df_decisions["NIVEL_RIESGO_EWI"] == "ROJO_CRITICO").sum())
        n_naranja = int((df_decisions["NIVEL_RIESGO_EWI"] == "NARANJA_MODERADO").sum())
        n_amarillo = int((df_decisions["NIVEL_RIESGO_EWI"] == "AMARILLO_VIGILANCIA").sum())
        n_verde = int((df_decisions["NIVEL_RIESGO_EWI"] == "VERDE_NORMAL").sum())

        pct_rojo = (n_rojo / max(1, total_eval)) * 100
        pct_naranja = (n_naranja / max(1, total_eval)) * 100
        pct_amarillo = (n_amarillo / max(1, total_eval)) * 100
        pct_verde = (n_verde / max(1, total_eval)) * 100

        st.markdown(f"""
        <div class="kpi-container">
            <div class="kpi-card-lux" style="border-left: 4px solid #10b981;">
                <div class="kpi-icon-wrapper" style="background: #ecfdf5; color: #059669;">🛡️</div>
                <div class="kpi-label">Verde (Normal)</div>
                <div class="kpi-big-value" style="color: #059669;">{n_verde:,}</div>
                <div class="kpi-pill kpi-pill-pos">{pct_verde:.1f}% de la cartera</div>
            </div>
            <div class="kpi-card-lux" style="border-left: 4px solid #f59e0b;">
                <div class="kpi-icon-wrapper" style="background: #fefce8; color: #d97706;">⚡</div>
                <div class="kpi-label">Amarillo (Vigilancia)</div>
                <div class="kpi-big-value" style="color: #d97706;">{n_amarillo:,}</div>
                <div class="kpi-pill kpi-pill-neutral">{pct_amarillo:.1f}% (1 alerta activa)</div>
            </div>
            <div class="kpi-card-lux" style="border-left: 4px solid #f97316;">
                <div class="kpi-icon-wrapper" style="background: #fff7ed; color: #ea580c;">⚠️</div>
                <div class="kpi-label">Naranja (Moderado)</div>
                <div class="kpi-big-value" style="color: #ea580c;">{n_naranja:,}</div>
                <div class="kpi-pill kpi-pill-neg">{pct_naranja:.1f}% (2 alertas activas)</div>
            </div>
            <div class="kpi-card-lux" style="border-left: 4px solid #ef4444;">
                <div class="kpi-icon-wrapper" style="background: #fef2f2; color: #dc2626;">🚨</div>
                <div class="kpi-label">Rojo (Estrés Crítico)</div>
                <div class="kpi-big-value" style="color: #dc2626;">{n_rojo:,}</div>
                <div class="kpi-pill kpi-pill-neg">{pct_rojo:.1f}% (≥3 alertas activas)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        ews_col1, ews_col2 = st.columns([1, 1])

        with ews_col1:
            st.markdown("#### 🍩 Distribución de Semáforo Preventivo EWS")
            df_ews_dist = df_decisions["NIVEL_RIESGO_EWI"].value_counts().reset_index()
            df_ews_dist.columns = ["Nivel", "Cuentas"]
            ews_colors = {
                "VERDE_NORMAL": "#10b981",
                "AMARILLO_VIGILANCIA": "#f59e0b",
                "NARANJA_MODERADO": "#f97316",
                "ROJO_CRITICO": "#ef4444"
            }
            fig_ews_donut = px.pie(
                df_ews_dist,
                names="Nivel",
                values="Cuentas",
                color="Nivel",
                color_discrete_map=ews_colors,
                hole=0.55
            )
            fig_ews_donut.update_traces(
                textposition='inside',
                textinfo='percent+label',
                marker=dict(line=dict(color='#ffffff', width=2))
            )
            fig_ews_donut.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=340,
                font=dict(family='Plus Jakarta Sans', size=11),
                showlegend=False
            )
            st.plotly_chart(fig_ews_donut, use_container_width=True)

        with ews_col2:
            st.markdown("#### 📊 Gatillos de Alerta Temprana Activados (EWIs)")
            ind_counts = ews_summary["ocurrencias_indicadores"]
            df_ind = pd.DataFrame([
                {"Indicador": "EWI 1: Uso Crítico (≥85%)", "Cuentas": ind_counts["uso_critico"], "Color": "#f97316"},
                {"Indicador": "EWI 2: Dependencia Mínimos (≥2)", "Cuentas": ind_counts["fatiga_minimos"], "Color": "#eab308"},
                {"Indicador": "EWI 3: Mora Incipiente (1-29d)", "Cuentas": ind_counts["mora_incipiente"], "Color": "#ef4444"},
                {"Indicador": "EWI 4: Vulnerabilidad / Sobregiro", "Cuentas": ind_counts["vulnerabilidad_presupuestal"], "Color": "#8b5cf6"}
            ])
            fig_ind = px.bar(
                df_ind,
                x="Cuentas",
                y="Indicador",
                orientation="h",
                color="Indicador",
                color_discrete_map={r["Indicador"]: r["Color"] for _, r in df_ind.iterrows()},
                text_auto=True
            )
            fig_ind.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=340,
                xaxis_title="Cuentas que detonan el indicador",
                yaxis_title="",
                font=dict(family='Plus Jakarta Sans', size=11),
                showlegend=False
            )
            st.plotly_chart(fig_ind, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 🎯 Matriz de Anticipación: Semáforo EWS vs Decisión de Política Actual")
        st.caption("Esta matriz cruzada revela clientes que actualmente se mantienen con crédito activo pero que el EWS ya detecta en estrés financiero incipiente.")
        
        cross_ews_dec = pd.crosstab(
            df_decisions["NIVEL_RIESGO_EWI"],
            df_decisions["DECISION_FINAL"],
            margins=True,
            margins_name="Total"
        )
        st.dataframe(cross_ews_dec, use_container_width=True)

        st.markdown("#### 📋 Padrón de Cuentas Bajo Vigilancia Preventiva")
        col_fil_ews1, col_fil_ews2 = st.columns([1, 2])
        with col_fil_ews1:
            filtro_nivel_ews = st.multiselect(
                "Filtrar por Nivel de Riesgo EWS:",
                options=["ROJO_CRITICO", "NARANJA_MODERADO", "AMARILLO_VIGILANCIA", "VERDE_NORMAL"],
                default=["ROJO_CRITICO", "NARANJA_MODERADO"]
            )
        
        df_ews_table = df_decisions[df_decisions["NIVEL_RIESGO_EWI"].isin(filtro_nivel_ews)]
        cols_ews_show = [
            "ID_CLIENTE", "SCORE_COMPORTAMENTAL", "PORC_USO_LINEA", "PAGOS_MINIMOS_CONSECUTIVOS",
            "DIAS_ATRASO_M1", "NUM_ALERTAS_EWI", "NIVEL_RIESGO_EWI", "ACCION_PREVENTIVA_EWI", "DECISION_FINAL"
        ]
        st.dataframe(df_ews_table[cols_ews_show], use_container_width=True, height=280)

    # -------------------------------------------------------------------------
    # TAB 4: EXPEDIENTE Y AUDITORÍA 360° (CASE REVIEW DE ALTO NIVEL)
    # -------------------------------------------------------------------------
    with tab4:
        st.subheader("Auditoría Individual de Cuenta (Expediente de Riesgo 360°)")
        
        cuenta_ids = df_decisions["ID_CLIENTE"].tolist()
        col_sel1, col_sel2 = st.columns([2, 1])
        with col_sel1:
            selected_client = st.selectbox("Seleccionar Identificador de Cliente para Inspección:", cuenta_ids, index=0)
            
        row = df_decisions[df_decisions["ID_CLIENTE"] == selected_client].iloc[0]
        
        # Color del badge según la regla
        badge_class = "dec-r0"
        if row["REGLA_DISPARADA"] == "R4_EXPANSION": badge_class = "dec-r4"
        elif row["REGLA_DISPARADA"] == "R3_MITIGACION": badge_class = "dec-r3"
        elif row["REGLA_DISPARADA"] == "R2_CONTENCION": badge_class = "dec-r2"
        elif row["REGLA_DISPARADA"] == "R1_KNOCKOUT": badge_class = "dec-r1"

        # Badge EWS
        ews_badge_class = "ews-verde"
        if row["NIVEL_RIESGO_EWI"] == "ROJO_CRITICO": ews_badge_class = "ews-rojo"
        elif row["NIVEL_RIESGO_EWI"] == "NARANJA_MODERADO": ews_badge_class = "ews-naranja"
        elif row["NIVEL_RIESGO_EWI"] == "AMARILLO_VIGILANCIA": ews_badge_class = "ews-amarillo"

        # Banner de veredicto
        st.markdown(f"""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <span class="badge-decision {badge_class}" style="font-size: 0.85rem; padding: 6px 14px;">{row['DECISION_FINAL']}</span>
                <span class="badge-ews {ews_badge_class}" style="font-size: 0.85rem; padding: 6px 14px; margin-left: 8px;">{row['NIVEL_RIESGO_EWI']}</span>
                <span style="margin-left: 10px; font-weight: 600; color: #475569;">Gatillo: <code>{row['REGLA_DISPARADA']}</code></span>
            </div>
            <div style="text-align: right;">
                <span style="font-size: 0.85rem; color: #64748b;">Código de Razón:</span>
                <code style="background: #e2e8f0; color: #0f172a; padding: 4px 8px; border-radius: 6px; font-weight: 600;">{row['CODIGO_RAZON']}</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_d1, col_d2 = st.columns([1, 1])

        with col_d1:
            st.markdown("#### Velocímetro de Score Comportamental")
            # Gauge Speedometer FICO
            score_val = int(row['SCORE_COMPORTAMENTAL'])
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score_val,
                title={'text': "<b>Calificación FICO Interna</b><br><span style='font-size:0.8em;color:#64748b'>Rango [300 - 850]</span>"},
                gauge={
                    'axis': {'range': [300, 850], 'tickwidth': 1, 'tickcolor': "#475569"},
                    'bar': {'color': "#0f172a", 'thickness': 0.3},
                    'bgcolor': "#f8fafc",
                    'steps': [
                        {'range': [300, 580], 'color': '#fee2e2'}, # Subprime
                        {'range': [580, 650], 'color': '#fef3c7'}, # Vulnerable
                        {'range': [650, 720], 'color': '#e0f2fe'}, # Moderado
                        {'range': [720, 850], 'color': '#d1fae5'}  # Prime
                    ],
                    'threshold': {
                        'line': {'color': "#059669", 'width': 4},
                        'thickness': 0.8,
                        'value': 720
                    }
                }
            ))
            fig_gauge.update_layout(height=290, margin=dict(t=30, b=10, l=30, r=30), font={'family': 'Plus Jakarta Sans'})
            st.plotly_chart(fig_gauge, use_container_width=True)

        with col_d2:
            st.markdown("#### Dimensionamiento de Línea de Crédito")
            st.markdown(f"""
            <div class="dossier-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.6rem;">
                    <span style="color: #64748b; font-weight: 500;">Contrato Asociado:</span>
                    <span style="font-family: 'JetBrains Mono', monospace; font-weight: 700;">{row['ID_CONTRATO']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.6rem;">
                    <span style="color: #64748b; font-weight: 500;">Línea Previa:</span>
                    <span style="font-weight: 700;">${row['LIMITE_CREDITO_ACTUAL']:,.2f} MXN</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.6rem;">
                    <span style="color: #64748b; font-weight: 500;">Saldo Actual Insoluto:</span>
                    <span style="font-weight: 700; color: #dc2626;">${row['SALDO_ACTUAL']:,.2f} MXN ({row['PORC_USO_LINEA']:.1f}%)</span>
                </div>
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 0.8rem 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.4rem;">
                    <span style="font-weight: 700; color: #0f172a;">Nuevo Límite Asignado:</span>
                    <span style="font-weight: 800; font-size: 1.15rem; color: #0284c7;">${row['NUEVO_LIMITE_CREDITO']:,.2f} MXN</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: 600; color: #64748b;">Delta de Exposición:</span>
                    <span style="font-weight: 700; color: {'#059669' if row['DELTA_EXPOSICION'] >= 0 else '#dc2626'};">
                        ${row['DELTA_EXPOSICION']:+,.2f} MXN
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Histórico de Morosidad Reciente (Vector Temporal)")
        col_m3, col_m2, col_m1, col_min, col_sob = st.columns(5)
        with col_m3:
            st.metric("Atraso Hace 3 Meses (M3)", f"{int(row['DIAS_ATRASO_M3'])} días")
        with col_m2:
            st.metric("Atraso Hace 2 Meses (M2)", f"{int(row['DIAS_ATRASO_M2'])} días")
        with col_m1:
            st.metric("Atraso Mes Actual (M1)", f"{int(row['DIAS_ATRASO_M1'])} días")
        with col_min:
            st.metric("Pagos Mínimos Consecutivos", f"{int(row['PAGOS_MINIMOS_CONSECUTIVOS'])}")
        with col_sob:
            st.metric("Sobregiros Últimos 6M", f"{int(row['NUM_SOBREGIROS_U6M'])}")

        # Panel de Alertas Tempranas del Cliente
        st.markdown(f"""
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.1rem; margin-top: 1rem; margin-bottom: 1rem;">
            <div style="font-weight: 700; color: #0f172a; font-size: 0.95rem; margin-bottom: 0.5rem;">
                🚨 Diagnóstico del Sistema de Alertas Tempranas (EWS)
            </div>
            <div style="font-size: 0.88rem; color: #475569; margin-bottom: 0.8rem;">
                <strong>Acción Preventiva Recomendada:</strong> <code>{row['ACCION_PREVENTIVA_EWI']}</code> &nbsp;•&nbsp; 
                <strong>Alertas Totales:</strong> <code>{row['NUM_ALERTAS_EWI']} / 4</code>
            </div>
            <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                <span class="kpi-pill {'kpi-pill-neg' if row['FLAG_EWI_USO'] else 'kpi-pill-pos'}">
                    {'🚨' if row['FLAG_EWI_USO'] else '✓'} Uso Crítico ({row['PORC_USO_LINEA']:.1f}%)
                </span>
                <span class="kpi-pill {'kpi-pill-neg' if row['FLAG_EWI_MINIMOS'] else 'kpi-pill-pos'}">
                    {'⚠️' if row['FLAG_EWI_MINIMOS'] else '✓'} Dependencia Mínimos ({int(row['PAGOS_MINIMOS_CONSECUTIVOS'])})
                </span>
                <span class="kpi-pill {'kpi-pill-neg' if row['FLAG_EWI_MORA_INCIPIENTE'] else 'kpi-pill-pos'}">
                    {'📉' if row['FLAG_EWI_MORA_INCIPIENTE'] else '✓'} Mora Incipiente ({int(row['DIAS_ATRASO_M1'])}d)
                </span>
                <span class="kpi-pill {'kpi-pill-neg' if row['FLAG_EWI_VULNERABILIDAD'] else 'kpi-pill-pos'}">
                    {'💳' if row['FLAG_EWI_VULNERABILIDAD'] else '✓'} Sobregiro/Reest ({int(row['NUM_SOBREGIROS_U6M'])} sob.)
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"💡 **Dictamen Regulatorio de Auditoría:** La cuenta `{row['ID_CONTRATO']}` fue evaluada bajo el árbol jerárquico de prelación de la política vigente. Se determinó la acción `{row['DECISION_FINAL']}` con código auditado `{row['CODIGO_RAZON']}`.")

    # -------------------------------------------------------------------------
    # TAB 5: CARTERA DECIDIDA Y LOGS DE AUDITORÍA
    # -------------------------------------------------------------------------
    with tab5:
        st.subheader("Registro de Auditoría Regulatoria y Exportación")
        
        col_fil1, col_fil2 = st.columns(2)
        with col_fil1:
            filtro_decision = st.multiselect(
                "Filtrar por Decisión:",
                options=df_decisions["DECISION_FINAL"].unique(),
                default=df_decisions["DECISION_FINAL"].unique()
            )
        with col_fil2:
            filtro_ews = st.multiselect(
                "Filtrar por Nivel de Riesgo EWS:",
                options=df_decisions["NIVEL_RIESGO_EWI"].unique(),
                default=df_decisions["NIVEL_RIESGO_EWI"].unique()
            )
        
        df_filtered = df_decisions[
            df_decisions["DECISION_FINAL"].isin(filtro_decision) &
            df_decisions["NIVEL_RIESGO_EWI"].isin(filtro_ews)
        ]
        
        cols_display = [
            "ID_CLIENTE", "SCORE_COMPORTAMENTAL", "LIMITE_CREDITO_ACTUAL", "SALDO_ACTUAL",
            "PORC_USO_LINEA", "DIAS_ATRASO_M1", "PAGOS_MINIMOS_CONSECUTIVOS",
            "NIVEL_RIESGO_EWI", "NUM_ALERTAS_EWI", "ACCION_PREVENTIVA_EWI",
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

    # -------------------------------------------------------------------------
    # TAB 6: SIMULACIÓN CHAMPION VS CHALLENGER (A/B TESTING AVANZADO)
    # -------------------------------------------------------------------------
    with tab6:
        st.subheader("Experimentación de Políticas: Metodología Champion vs Challenger")
        st.markdown("""
        En la ingeniería de motores de decisión bancaria, las políticas de riesgo se evalúan bajo el framework **Champion/Challenger**:
        - **Champion:** Política probada actualmente en producción (línea base).
        - **Challenger:** Política retadora con hipótesis de reducción de mora o expansión controlada.
        """)

        col_c_cfg1, col_c_cfg2 = st.columns(2)
        with col_c_cfg1:
            st.markdown("#### Configuración de Política Retadora (Challenger)")
            challenger_preset = st.selectbox(
                "Seleccionar Escenario Challenger:",
                [
                    "Challenger Conservador (Knock-out a 60 días, Score Prime 750)",
                    "Challenger Expansivo (Score Prime 700, Aumento +35% agresivo)",
                    "Challenger Anti-Mora (Contención urgente a 20 días mora)"
                ]
            )

            if "Conservador" in challenger_preset:
                p_challenger = PolicyParameters(
                    dias_mora_default=60,
                    score_prime=750,
                    factor_reduccion_linea=0.50
                )
            elif "Expansivo" in challenger_preset:
                p_challenger = PolicyParameters(
                    dias_mora_default=90,
                    score_prime=700,
                    factor_incremento_linea=1.35,
                    uso_max_expansion=85.0
                )
            else: # Anti-mora
                p_challenger = PolicyParameters(
                    dias_mora_default=75,
                    dias_mora_contencion=20,
                    uso_linea_critico=90.0
                )
            p_challenger.habilitar_matriz_dinamica = True

        with col_c_cfg2:
            st.markdown("#### Distribución de Tráfico A/B")
            split_pct = st.slider("Asignación de Cartera a Champion (%):", 50, 95, 80, 5)
            st.write(f"- **Champion:** `{split_pct}%` de la cartera")
            st.write(f"- **Challenger:** `{100 - split_pct}%` de la cartera")

        simulator = ChampionChallengerSimulator(
            champion_params=policy_params,
            challenger_params=p_challenger,
            split_ratio=split_pct / 100.0
        )

        df_ab_result, kpis_ab = simulator.simulate_split(df_features)

        st.markdown("---")
        st.markdown("#### Comparación de Impacto: Champion vs Challenger")

        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        with kpi_col1:
            st.metric("Tasa Incremento (Champion)", f"{kpis_ab['tasas_champion']['tasa_aumento_pct']}%")
        with kpi_col2:
            st.metric("Tasa Incremento (Challenger)", f"{kpis_ab['tasas_challenger']['tasa_aumento_pct']}%",
                      delta=f"{kpis_ab['tasas_challenger']['tasa_aumento_pct'] - kpis_ab['tasas_champion']['tasa_aumento_pct']:+.2f}%")
        with kpi_col3:
            st.metric("Tasa Contención (Champion)", f"{kpis_ab['tasas_champion']['tasa_bloqueo_pct']}%")
        with kpi_col4:
            st.metric("Tasa Contención (Challenger)", f"{kpis_ab['tasas_challenger']['tasa_bloqueo_pct']}%",
                      delta=f"{kpis_ab['tasas_challenger']['tasa_bloqueo_pct'] - kpis_ab['tasas_champion']['tasa_bloqueo_pct']:+.2f}%", delta_color="inverse")

        # Gráfica comparativa estilizada
        df_comp_chart = pd.DataFrame({
            "Métrica": ["Aumento Línea", "Mantenimiento", "Reducción", "Bloqueo Mora", "Cancelación Default"],
            "Champion (%)": [
                kpis_ab['tasas_champion']['tasa_aumento_pct'],
                kpis_ab['tasas_champion']['tasa_mantenimiento_pct'],
                kpis_ab['tasas_champion']['tasa_reduccion_pct'],
                kpis_ab['tasas_champion']['tasa_bloqueo_pct'],
                kpis_ab['tasas_champion']['tasa_cancelacion_pct']
            ],
            "Challenger (%)": [
                kpis_ab['tasas_challenger']['tasa_aumento_pct'],
                kpis_ab['tasas_challenger']['tasa_mantenimiento_pct'],
                kpis_ab['tasas_challenger']['tasa_reduccion_pct'],
                kpis_ab['tasas_challenger']['tasa_bloqueo_pct'],
                kpis_ab['tasas_challenger']['tasa_cancelacion_pct']
            ]
        })

        fig_ab = go.Figure(data=[
            go.Bar(name='Champion (Línea Base)', x=df_comp_chart["Métrica"], y=df_comp_chart["Champion (%)"], marker_color='#3b82f6'),
            go.Bar(name='Challenger (Retadora)', x=df_comp_chart["Métrica"], y=df_comp_chart["Challenger (%)"], marker_color='#8b5cf6')
        ])
        fig_ab.update_layout(
            barmode='group',
            height=370,
            margin=dict(t=20, b=20, l=20, r=20),
            yaxis_title="% de Cartera",
            font=dict(family='Plus Jakarta Sans', size=11)
        )
        st.plotly_chart(fig_ab, use_container_width=True)

        st.info("💡 **Conclusión Metodológica para Comités:** Si la estrategia Challenger demuestra mitigar mayor volumen de riesgo sin sacrificar la rentabilidad de clientes Prime durante el periodo de prueba, el comité puede promover formalmente el Challenger a nuevo Champion.")

else:
    st.warning("No se ha cargado ninguna cartera crediticia. Seleccione una fuente en la barra lateral.")
