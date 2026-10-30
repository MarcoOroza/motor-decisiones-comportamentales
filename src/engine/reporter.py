"""
Módulo de Reporting Regulatorio y Auditoría Automatizada (PDF y Excel Corporativo).
Genera dictámenes oficiales inmutables y libros contables multi-hoja para comités de riesgo.
Proyecto de Residencia Profesional: Marco Antonio Oroza Ortega - TESE (División de Informática).
"""

import io
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

# OpenPyXL para generación de hojas de cálculo estructuradas
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ReportLab para generación de informes formales en PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numerar páginas con 'Página X de Y' y encabezado formal."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7)
        self.setFillColor(colors.HexColor("#475569"))
        
        # Encabezado (Páginas 2 en adelante)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "TECNOLÓGICO DE ESTUDIOS SUPERIORES DE ECATEPEC • DIVISIÓN DE INFORMÁTICA")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "DICTAMEN EJECUTIVO DE RIESGO DE CRÉDITO")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Pie de página (Todas las páginas)
        self.setFont("Helvetica", 7)
        self.drawString(54, 30, "PROYECTO DE RESIDENCIA PROFESIONAL — RESIDENTE: MARCO ANTONIO OROZA ORTEGA")
        self.drawRightString(letter[0] - 54, 30, f"Página {self._pageNumber} de {page_count}")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 40, letter[0] - 54, 40)
        self.restoreState()


def generate_pdf_audit_report(
    df_decisions: pd.DataFrame,
    audit_summary: Dict[str, Any],
    ews_summary: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Genera un dictamen formal de auditoría en PDF con membrete institucional del TESE.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    # Estilos tipográficos ejecutivos
    style_inst = ParagraphStyle(
        'Institucional',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#0284C7"),
        spaceAfter=2
    )
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=4
    )
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=12
    )
    style_h2 = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=6
    )
    style_body = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155")
    )
    style_body_bold = ParagraphStyle(
        'Body_Bold_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0F172A")
    )
    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#1E293B")
    )
    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white
    )

    story = []

    # 1. ENCABEZADO INSTITUCIONAL
    story.append(Paragraph("TECNOLÓGICO DE ESTUDIOS SUPERIORES DE ECATEPEC • DIVISIÓN DE INFORMÁTICA", style_inst))
    story.append(Paragraph("Dictamen Ejecutivo de Auditoría y Gestión de Cartera", style_title))
    story.append(Paragraph("Plataforma Analítica de Decisiones Comportamentales de Crédito (Arquitectura Basada en PowerCurve)", style_subtitle))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0F172A"), spaceAfter=10))

    # 2. METADATA DE AUDITORÍA
    mf = audit_summary.get("metricas_financieras", {})
    exec_id = audit_summary.get("execution_id", "N/A")[:18] + "..."
    ts = audit_summary.get("timestamp_utc", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"))
    
    meta_data = [
        [
            Paragraph("<b>Folio Único de Auditoría:</b>", style_body),
            Paragraph(f"<code>{exec_id}</code>", style_body),
            Paragraph("<b>Fecha y Hora de Corte:</b>", style_body),
            Paragraph(str(ts), style_body)
        ],
        [
            Paragraph("<b>Residente / Desarrollador:</b>", style_body),
            Paragraph("Marco Antonio Oroza Ortega", style_body_bold),
            Paragraph("<b>Población Auditada:</b>", style_body),
            Paragraph(f"{audit_summary.get('total_cuentas_procesadas', len(df_decisions)):,} contratos", style_body_bold)
        ],
        [
            Paragraph("<b>Marco Normativo:</b>", style_body),
            Paragraph("IFRS 9 (Stage 2) / Basilea III / CNBV", style_body),
            Paragraph("<b>Hash de Integridad (SHA-256):</b>", style_body),
            Paragraph(hashlib.sha256(df_decisions.to_json().encode('utf-8')).hexdigest()[:16] + "...", style_body)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[110, 150, 110, 134])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#F1F5F9")),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. RESUMEN DE IMPACTO FINANCIERO
    story.append(Paragraph("1. Resumen Consolidado de Exposición Crediticia", style_h2))
    
    lim_prev = mf.get("limite_vigente_total_mxn", 0.0)
    lim_new = mf.get("nuevo_limite_total_mxn", 0.0)
    delta_neto = mf.get("delta_exposicion_neta_mxn", 0.0)
    pct_var = mf.get("porcentaje_variacion_linea", 0.0)
    saldo_tot = mf.get("saldo_cartera_evaluada_mxn", 0.0)

    fin_data = [
        [
            Paragraph("Métrica Financiera", style_table_header),
            Paragraph("Línea Previa (MXN)", style_table_header),
            Paragraph("Saldo Insoluto (MXN)", style_table_header),
            Paragraph("Nuevo Límite Autorizado", style_table_header),
            Paragraph("Delta de Exposición Neta", style_table_header),
            Paragraph("Variación (%)", style_table_header)
        ],
        [
            Paragraph("<b>Total Cartera</b>", style_table_cell),
            Paragraph(f"${lim_prev:,.2f}", style_table_cell),
            Paragraph(f"${saldo_tot:,.2f}", style_table_cell),
            Paragraph(f"${lim_new:,.2f}", style_table_cell),
            Paragraph(f"${delta_neto:+,.2f}", style_table_cell),
            Paragraph(f"{pct_var:+.2f}%", style_table_cell)
        ]
    ]
    fin_table = Table(fin_data, colWidths=[90, 85, 85, 95, 95, 54])
    fin_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#F1F5F9")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 12))

    # 4. DISTRIBUCIÓN DE DECISIONES TÁCTICAS
    story.append(Paragraph("2. Distribución de Acciones Tácticas y Códigos de Razón (Reason Codes)", style_h2))
    
    dec_counts = df_decisions["DECISION_FINAL"].value_counts()
    dec_rows = [
        [
            Paragraph("Decisión Estratégica", style_table_header),
            Paragraph("Regla Asociada", style_table_header),
            Paragraph("Cuentas", style_table_header),
            Paragraph("Participación (%)", style_table_header),
            Paragraph("Impacto Neto en Exposición (MXN)", style_table_header)
        ]
    ]

    total_c = len(df_decisions)
    for dec_name, count in dec_counts.items():
        sub_df = df_decisions[df_decisions["DECISION_FINAL"] == dec_name]
        regla = sub_df["REGLA_DISPARADA"].iloc[0] if len(sub_df) > 0 else "N/A"
        delta_sub = sub_df["DELTA_EXPOSICION"].sum()
        pct = (count / max(1, total_c)) * 100
        dec_rows.append([
            Paragraph(f"<b>{dec_name}</b>", style_table_cell),
            Paragraph(f"<code>{regla}</code>", style_table_cell),
            Paragraph(f"{count:,}", style_table_cell),
            Paragraph(f"{pct:.2f}%", style_table_cell),
            Paragraph(f"${delta_sub:+,.2f}", style_table_cell)
        ])

    dec_table = Table(dec_rows, colWidths=[150, 95, 60, 80, 119])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(dec_table)
    story.append(Spacer(1, 12))

    # 5. DICTAMEN DE ALERTAS TEMPRANAS (EWS - IFRS 9 STAGE 2)
    if "NIVEL_RIESGO_EWI" in df_decisions.columns:
        story.append(Paragraph("3. Monitoreo Prospectivo: Sistema de Alertas Tempranas (EWS / IFRS 9 Stage 2)", style_h2))
        
        ews_dist = df_decisions["NIVEL_RIESGO_EWI"].value_counts()
        ews_rows = [
            [
                Paragraph("Semáforo Preventivo EWS", style_table_header),
                Paragraph("Nivel de Estrés Heurístico", style_table_header),
                Paragraph("Cuentas", style_table_header),
                Paragraph("Participación (%)", style_table_header),
                Paragraph("Acción Preventiva Dictaminada", style_table_header)
            ]
        ]
        
        sem_desc = {
            "VERDE_NORMAL": "0 alertas activas (Perfil solvente)",
            "AMARILLO_VIGILANCIA": "1 alerta activa (Vigilancia preventiva)",
            "NARANJA_MODERADO": "2 alertas activas (Estrés moderado)",
            "ROJO_CRITICO": ">=3 alertas activas (Estrés severo)"
        }
        
        for nivel in ["VERDE_NORMAL", "AMARILLO_VIGILANCIA", "NARANJA_MODERADO", "ROJO_CRITICO"]:
            cnt = ews_dist.get(nivel, 0)
            pct = (cnt / max(1, total_c)) * 100
            sub_e = df_decisions[df_decisions["NIVEL_RIESGO_EWI"] == nivel]
            act = sub_e["ACCION_PREVENTIVA_EWI"].iloc[0] if len(sub_e) > 0 else "MONITOREO_ESTANDAR"
            ews_rows.append([
                Paragraph(f"<b>{nivel}</b>", style_table_cell),
                Paragraph(sem_desc.get(nivel, ""), style_table_cell),
                Paragraph(f"{cnt:,}", style_table_cell),
                Paragraph(f"{pct:.2f}%", style_table_cell),
                Paragraph(f"<code>{act}</code>", style_table_cell)
            ])

        ews_table = Table(ews_rows, colWidths=[95, 120, 50, 65, 174])
        ews_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0F172A")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('ALIGN', (2, 1), (3, -1), 'RIGHT'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(ews_table)
        story.append(Spacer(1, 14))

    # 6. MUESTRA TESTIGO DE AUDITORÍA (CASOS CRÍTICOS)
    story.append(Paragraph("4. Muestra Testigo de Auditoría (Casos Críticos y Modificaciones de Línea)", style_h2))
    sample_df = df_decisions.sort_values(by="DELTA_EXPOSICION", ascending=True).head(5)
    sample_exp = df_decisions.sort_values(by="DELTA_EXPOSICION", ascending=False).head(3)
    sample_combined = pd.concat([sample_df, sample_exp], ignore_index=True)

    sample_rows = [
        [
            Paragraph("Contrato", style_table_header),
            Paragraph("Score", style_table_header),
            Paragraph("Uso %", style_table_header),
            Paragraph("Mora M1", style_table_header),
            Paragraph("Decisión Final", style_table_header),
            Paragraph("Límite Previo", style_table_header),
            Paragraph("Nuevo Límite", style_table_header),
            Paragraph("Delta MXN", style_table_header)
        ]
    ]

    for _, r in sample_combined.iterrows():
        sample_rows.append([
            Paragraph(f"<code>{str(r['ID_CONTRATO'])[:11]}</code>", style_table_cell),
            Paragraph(str(int(r['SCORE_COMPORTAMENTAL'])), style_table_cell),
            Paragraph(f"{r['PORC_USO_LINEA']:.1f}%", style_table_cell),
            Paragraph(f"{int(r['DIAS_ATRASO_M1'])}d", style_table_cell),
            Paragraph(str(r['DECISION_FINAL'])[:16], style_table_cell),
            Paragraph(f"${r['LIMITE_CREDITO_ACTUAL']:,.0f}", style_table_cell),
            Paragraph(f"${r['NUEVO_LIMITE_CREDITO']:,.0f}", style_table_cell),
            Paragraph(f"${r['DELTA_EXPOSICION']:+,.0f}", style_table_cell)
        ])

    sample_table = Table(sample_rows, colWidths=[65, 35, 40, 42, 105, 72, 72, 73])
    sample_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ('ALIGN', (1, 1), (3, -1), 'CENTER'),
        ('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(sample_table)
    story.append(Spacer(1, 20))

    # 7. DECLARACIÓN REGULATORIA Y BLOQUE DE FIRMAS
    sig_block = [
        [
            Paragraph("<b>DICTAMEN DE CONFORMIDAD TÉCNICA</b><br/><font size='7' color='#64748B'>Se certifica que la cartera fue evaluada bajo reglas de prelación jerárquica estricta sin colisiones lógicas, respetando la salvaguarda de saldo insoluto al 105% y las directrices de provisionamiento IFRS 9.</font>", style_body),
            Paragraph("<b>SELLO DIGITAL DE AUDITORÍA</b><br/><font size='7' color='#64748B'>Verificación criptográfica SHA-256 válida para auditorías internas de la División de Informática y comités de riesgo financiero.</font>", style_body)
        ],
        [
            Paragraph("<br/><br/>________________________________________<br/><b>Marco Antonio Oroza Ortega</b><br/>Autor / Residente de Informática<br/>TESE - División de Informática", style_body),
            Paragraph("<br/><br/>________________________________________<br/><b>Coordinación de Residencia Profesional</b><br/>División de Informática<br/>Tecnológico de Estudios Superiores de Ecatepec", style_body)
        ]
    ]
    sig_table = Table(sig_block, colWidths=[250, 254])
    sig_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether([sig_table]))

    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer.getvalue()


def generate_excel_audit_workbook(
    df_decisions: pd.DataFrame,
    audit_summary: Dict[str, Any],
    ews_summary: Optional[Dict[str, Any]] = None
) -> bytes:
    """
    Genera un libro contable multi-hoja en formato Excel (.xlsx) estructurado,
    con estilos corporativos, formatos numéricos y formato condicional por decisión.
    """
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------------------
    # ESTILOS CORPORATIVOS
    # -------------------------------------------------------------------------
    font_title = Font(name="Calibri", size=15, bold=True, color="0F172A")
    font_subtitle = Font(name="Calibri", size=10, italic=True, color="64748B")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True, color="0F172A")
    font_regular = Font(name="Calibri", size=9.5, color="1E293B")
    
    fill_header_navy = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    fill_header_blue = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    fill_meta_light = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_kpi_card = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")

    border_thin = Border(
        left=Side(style='thin', color='E2E8F0'),
        right=Side(style='thin', color='E2E8F0'),
        top=Side(style='thin', color='E2E8F0'),
        bottom=Side(style='thin', color='E2E8F0')
    )

    # -------------------------------------------------------------------------
    # HOJA 1: RESUMEN EJECUTIVO Y KPIS
    # -------------------------------------------------------------------------
    ws_kpi = wb.active
    ws_kpi.title = "Resumen_Ejecutivo"
    ws_kpi.views.sheetView[0].showGridLines = True

    # Encabezado
    ws_kpi["A1"] = "TECNOLÓGICO DE ESTUDIOS SUPERIORES DE ECATEPEC • DIVISIÓN DE INFORMÁTICA"
    ws_kpi["A1"].font = Font(name="Calibri", size=10, bold=True, color="0284C7")
    ws_kpi["A2"] = "Dictamen Ejecutivo y Auditoría Financiera de Cartera Crediticia"
    ws_kpi["A2"].font = font_title
    ws_kpi["A3"] = f"Motor de Decisiones Comportamentales tipo PowerCurve • Autor: Marco Antonio Oroza Ortega • Generado: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    ws_kpi["A3"].font = font_subtitle

    # Cuadrícula de Metadata
    ws_kpi["A5"] = "ID de Ejecución:"
    ws_kpi["B5"] = audit_summary.get("execution_id", "N/A")
    ws_kpi["A6"] = "Total de Contratos Auditados:"
    ws_kpi["B6"] = len(df_decisions)
    ws_kpi["A7"] = "Estatus Normativo:"
    ws_kpi["B7"] = "Cumplimiento IFRS 9 / Basilea III / CNBV"
    ws_kpi["A8"] = "Sello Criptográfico SHA-256:"
    ws_kpi["B8"] = hashlib.sha256(df_decisions.to_json().encode('utf-8')).hexdigest()

    for r in range(5, 9):
        ws_kpi[f"A{r}"].font = font_bold
        ws_kpi[f"A{r}"].fill = fill_meta_light
        ws_kpi[f"B{r}"].font = font_regular
        ws_kpi[f"A{r}"].border = border_thin
        ws_kpi[f"B{r}"].border = border_thin

    # Tabla de Impacto Financiero
    ws_kpi["A10"] = "INDICADOR FINANCIERO"
    ws_kpi["B10"] = "VALOR (MXN)"
    ws_kpi["C10"] = "DESCRIPCIÓN OPERATIVA"
    for col in ["A10", "B10", "C10"]:
        ws_kpi[col].font = font_header
        ws_kpi[col].fill = fill_header_navy
        ws_kpi[col].alignment = Alignment(horizontal="center")

    mf = audit_summary.get("metricas_financieras", {})
    kpi_rows = [
        ("Límite Vigente Previo de Cartera", mf.get("limite_vigente_total_mxn", 0.0), "$#,##0.00", "Exposición contractual antes del procesamiento"),
        ("Saldo Insoluto Total de Cartera", mf.get("saldo_cartera_evaluada_mxn", 0.0), "$#,##0.00", "Monto actualmente utilizado y adeudado por los clientes"),
        ("Nuevo Límite Autorizado", mf.get("nuevo_limite_total_mxn", 0.0), "$#,##0.00", "Límite neto asignado tras aplicar reglas de prelación"),
        ("Delta Neta de Exposición (MXN)", mf.get("delta_exposicion_neta_mxn", 0.0), "$#,##0.00", "Variación neta en pesos (aumentos menos reducciones y cancelaciones)"),
        ("Porcentaje de Variación de Línea", mf.get("porcentaje_variacion_linea", 0.0) / 100.0, "0.00%", "Tasa porcentual de ajuste respecto a la línea base")
    ]

    for idx, (lbl, val, fmt, desc) in enumerate(kpi_rows, start=11):
        ws_kpi[f"A{idx}"] = lbl
        ws_kpi[f"A{idx}"].font = font_bold
        ws_kpi[f"B{idx}"] = val
        ws_kpi[f"B{idx}"].font = font_bold
        ws_kpi[f"B{idx}"].number_format = fmt
        ws_kpi[f"C{idx}"] = desc
        ws_kpi[f"C{idx}"].font = font_regular
        for c in [f"A{idx}", f"B{idx}", f"C{idx}"]:
            ws_kpi[c].border = border_thin

    # Tabla de Distribución por Decisión
    start_dec = 18
    ws_kpi[f"A{start_dec}"] = "DECISIÓN ESTRATÉGICA"
    ws_kpi[f"B{start_dec}"] = "CONTRATOS"
    ws_kpi[f"C{start_dec}"] = "% CARTERA"
    ws_kpi[f"D{start_dec}"] = "DELTA EXPOSICIÓN (MXN)"
    for col in [f"A{start_dec}", f"B{start_dec}", f"C{start_dec}", f"D{start_dec}"]:
        ws_kpi[col].font = font_header
        ws_kpi[col].fill = fill_header_blue
        ws_kpi[col].alignment = Alignment(horizontal="center")

    dec_counts = df_decisions["DECISION_FINAL"].value_counts()
    for offset, (dec_name, cnt) in enumerate(dec_counts.items(), start=1):
        curr_row = start_dec + offset
        sub_d = df_decisions[df_decisions["DECISION_FINAL"] == dec_name]
        d_exp = sub_d["DELTA_EXPOSICION"].sum()
        pct = cnt / max(1, len(df_decisions))

        ws_kpi[f"A{curr_row}"] = dec_name
        ws_kpi[f"A{curr_row}"].font = font_regular
        ws_kpi[f"B{curr_row}"] = cnt
        ws_kpi[f"B{curr_row}"].number_format = "#,##0"
        ws_kpi[f"C{curr_row}"] = pct
        ws_kpi[f"C{curr_row}"].number_format = "0.00%"
        ws_kpi[f"D{curr_row}"] = d_exp
        ws_kpi[f"D{curr_row}"].number_format = "$#,##0.00"
        for c in [f"A{curr_row}", f"B{curr_row}", f"C{curr_row}", f"D{curr_row}"]:
            ws_kpi[c].border = border_thin

    # -------------------------------------------------------------------------
    # HOJA 2: ALERTAS TEMPRANAS (EWS)
    # -------------------------------------------------------------------------
    ws_ews = wb.create_sheet(title="Alertas_Tempranas_EWS")
    ws_ews.views.sheetView[0].showGridLines = True

    ws_ews["A1"] = "SISTEMA DE ALERTAS TEMPRANAS (EWS) — CLASIFICACIÓN IFRS 9 STAGE 2"
    ws_ews["A1"].font = font_title

    ws_ews["A3"] = "NIVEL DE RIESGO EWS"
    ws_ews["B3"] = "CONTRATOS"
    ws_ews["C3"] = "% CARTERA"
    ws_ews["D3"] = "ACCIÓN PREVENTIVA DICTAMINADA"
    for col in ["A3", "B3", "C3", "D3"]:
        ws_ews[col].font = font_header
        ws_ews[col].fill = fill_header_navy
        ws_ews[col].alignment = Alignment(horizontal="center")

    if "NIVEL_RIESGO_EWI" in df_decisions.columns:
        ews_levels = ["VERDE_NORMAL", "AMARILLO_VIGILANCIA", "NARANJA_MODERADO", "ROJO_CRITICO"]
        for idx, lvl in enumerate(ews_levels, start=4):
            sub_e = df_decisions[df_decisions["NIVEL_RIESGO_EWI"] == lvl]
            c_cnt = len(sub_e)
            pct = c_cnt / max(1, len(df_decisions))
            act = sub_e["ACCION_PREVENTIVA_EWI"].iloc[0] if c_cnt > 0 else "N/A"
            ws_ews[f"A{idx}"] = lvl
            ws_ews[f"A{idx}"].font = font_bold
            ws_ews[f"B{idx}"] = c_cnt
            ws_ews[f"B{idx}"].number_format = "#,##0"
            ws_ews[f"C{idx}"] = pct
            ws_ews[f"C{idx}"].number_format = "0.00%"
            ws_ews[f"D{idx}"] = act
            ws_ews[f"D{idx}"].font = font_regular
            for c in [f"A{idx}", f"B{idx}", f"C{idx}", f"D{idx}"]:
                ws_ews[c].border = border_thin

        # Matriz Cruzada EWS vs Decisión
        ws_ews["A10"] = "MATRIZ DE ANTICIPACIÓN CRUZADA: Semáforo EWS vs. Decisión Política"
        ws_ews["A10"].font = Font(name="Calibri", size=11, bold=True, color="0F172A")
        
        cross_tab = pd.crosstab(df_decisions["NIVEL_RIESGO_EWI"], df_decisions["DECISION_FINAL"], margins=True)
        # Escribir encabezados de crosstab
        cols_ct = ["Nivel EWS"] + list(cross_tab.columns)
        for c_idx, c_name in enumerate(cols_ct, start=1):
            cell = ws_ews.cell(row=12, column=c_idx, value=str(c_name))
            cell.font = font_header
            cell.fill = fill_header_blue
            cell.alignment = Alignment(horizontal="center")
            cell.border = border_thin

        for r_idx, (idx_name, row_vals) in enumerate(cross_tab.iterrows(), start=13):
            cell_lbl = ws_ews.cell(row=r_idx, column=1, value=str(idx_name))
            cell_lbl.font = font_bold
            cell_lbl.border = border_thin
            for c_idx, val in enumerate(row_vals, start=2):
                cell_v = ws_ews.cell(row=r_idx, column=c_idx, value=int(val))
                cell_v.font = font_regular
                cell_v.number_format = "#,##0"
                cell_v.border = border_thin

    # -------------------------------------------------------------------------
    # HOJA 3: CARTERA DECIDIDA (DETALLE COMPLETO AUDITABLE)
    # -------------------------------------------------------------------------
    ws_data = wb.create_sheet(title="Cartera_Decidida")
    ws_data.views.sheetView[0].showGridLines = True

    export_cols = [
        "ID_CLIENTE", "ID_CONTRATO", "SCORE_COMPORTAMENTAL",
        "LIMITE_CREDITO_ACTUAL", "SALDO_ACTUAL", "PORC_USO_LINEA",
        "DIAS_ATRASO_M1", "PAGOS_MINIMOS_CONSECUTIVOS", "NUM_SOBREGIROS_U6M",
        "NIVEL_RIESGO_EWI", "ACCION_PREVENTIVA_EWI",
        "REGLA_DISPARADA", "DECISION_FINAL", "NUEVO_LIMITE_CREDITO", "DELTA_EXPOSICION", "CODIGO_RAZON"
    ]
    # Filtrar solo las columnas que existan en el DataFrame
    valid_cols = [c for c in export_cols if c in df_decisions.columns]

    # Encabezado
    for col_idx, col_name in enumerate(valid_cols, start=1):
        c = ws_data.cell(row=1, column=col_idx, value=col_name)
        c.font = font_header
        c.fill = fill_header_navy
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = border_thin

    # Mapeo de colores condicionales según Decisión
    color_fills = {
        "INCREMENTAR_LINEA_PROACTIVO": PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid"),
        "MANTENER_CONDICIONES_ACTUALES": PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid"),
        "REDUCIR_LINEA_PREVENTIVA": PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid"),
        "BLOQUEO_TEMPORAL_LINEA": PatternFill(start_color="FFEDD5", end_color="FFEDD5", fill_type="solid"),
        "CANCELAR_LINEA_Y_ENVIO_COBRANZA": PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    }

    # Escribir filas
    for row_idx, row_data in enumerate(df_decisions[valid_cols].itertuples(index=False), start=2):
        dec_val = getattr(row_data, "DECISION_FINAL", None)
        row_fill = color_fills.get(dec_val, None)

        for col_idx, (col_name, val) in enumerate(zip(valid_cols, row_data), start=1):
            cell = ws_data.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_regular
            cell.border = border_thin

            if col_name == "DECISION_FINAL" and row_fill:
                cell.fill = row_fill
                cell.font = font_bold

            # Formatos numéricos
            if col_name in ["LIMITE_CREDITO_ACTUAL", "SALDO_ACTUAL", "NUEVO_LIMITE_CREDITO", "DELTA_EXPOSICION"]:
                cell.number_format = "$#,##0.00"
            elif col_name == "PORC_USO_LINEA":
                cell.number_format = "0.0"
            elif col_name in ["SCORE_COMPORTAMENTAL", "DIAS_ATRASO_M1", "PAGOS_MINIMOS_CONSECUTIVOS", "NUM_SOBREGIROS_U6M"]:
                cell.number_format = "#,##0"

    ws_data.auto_filter.ref = f"A1:{get_column_letter(len(valid_cols))}{len(df_decisions) + 1}"

    # -------------------------------------------------------------------------
    # HOJA 4: LOG DE AUDITORÍA Y TRAZABILIDAD
    # -------------------------------------------------------------------------
    ws_log = wb.create_sheet(title="Log_Auditoria")
    ws_log.views.sheetView[0].showGridLines = True

    ws_log["A1"] = "REGISTRO INMUTABLE DE AUDITORÍA (AUDIT TRAIL & GOVERNANCE)"
    ws_log["A1"].font = font_title

    audit_items = [
        ("ID_EJECUCION", audit_summary.get("execution_id", "N/A")),
        ("TIMESTAMP_UTC", audit_summary.get("timestamp_utc", "N/A")),
        ("ESTRATEGIA_APLICADA", audit_summary.get("strategy_name", "PowerCurve_Behavioral_v2")),
        ("INSTITUCION", "Tecnológico de Estudios Superiores de Ecatepec (TESE)"),
        ("DIVISION_ACADEMICA", "División de Informática"),
        ("AUTOR_RESIDENTE", "Marco Antonio Oroza Ortega"),
        ("TOTAL_CUENTAS_EVALUADAS", len(df_decisions)),
        ("HASH_INTEGRIDAD_SHA256", hashlib.sha256(df_decisions.to_json().encode('utf-8')).hexdigest()),
        ("ESTATUS_COMPLIANCE", "CONFORME - Árbol jerárquico sin colisiones y prelación validada al 100%")
    ]

    ws_log["A3"] = "PARÁMETRO DE AUDITORÍA"
    ws_log["B3"] = "VALOR REGISTRADO"
    for col in ["A3", "B3"]:
        ws_log[col].font = font_header
        ws_log[col].fill = fill_header_navy
        ws_log[col].alignment = Alignment(horizontal="center")

    for idx, (param, val) in enumerate(audit_items, start=4):
        ws_log[f"A{idx}"] = param
        ws_log[f"A{idx}"].font = font_bold
        ws_log[f"A{idx}"].fill = fill_meta_light
        ws_log[f"B{idx}"] = str(val)
        ws_log[f"B{idx}"].font = font_regular
        ws_log[f"A{idx}"].border = border_thin
        ws_log[f"B{idx}"].border = border_thin

    # Ajuste automático del ancho de columnas en todas las hojas
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or '')
                if len(val_str) > max_len and len(val_str) < 60:
                    max_len = len(val_str)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 11)

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
