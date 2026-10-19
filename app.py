import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
import datetime

# Importar módulos de negocio
from modules.lft_rules import LFTRulesEngine
from modules.simulator_40h import ReformSimulator
from modules.sap_exporter import SAPHCMExporter
from modules.ai_advisor import CatchAIAdvisor

# Configuración de página de Streamlit con favicon oficial de Catch Consulting
st.set_page_config(
    page_title="Catch Workforce 40 | Plataforma de Inteligencia Laboral",
    page_icon="https://www.catchconsulting.com.mx/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar logo SVG vectorial de Catch Consulting
svg_logo_raw = ""
logo_path = os.path.join(os.path.dirname(__file__), "catch_logo.svg")
if os.path.exists(logo_path):
    try:
        with open(logo_path, "r", encoding="utf-8") as f:
            svg_logo_raw = f.read()
    except Exception:
        svg_logo_raw = ""

# Paleta oficial de colores Catch Consulting
CATCH_PALETTE = ['#3AB0CD', '#1C242F', '#0C8489', '#5EBED1', '#64748B', '#F1A720', '#E92736']

def apply_catch_theme(fig):
    """Aplica la estética limpia y corporativa de Catch Consulting a gráficos de Plotly."""
    fig.update_layout(
        font=dict(family="Inter, sans-serif", color="#1C242F"),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        xaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", title_font=dict(family="Inter", size=12)),
        yaxis=dict(gridcolor="#F1F5F9", zerolinecolor="#E2E8F0", title_font=dict(family="Inter", size=12))
    )
    return fig

# Inyección de estilos CSS basados directamente en https://www.catchconsulting.com.mx/
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Lexend:wght@400;500;600;700;800&display=swap');

    /* Tipografía y colores base */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1C242F !important;
        background-color: #FFFFFF !important;
    }

    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lexend', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #1C242F !important;
        letter-spacing: -0.02em;
        font-weight: 600;
    }

    .main-header {
        font-family: 'Lexend', sans-serif;
        font-size: 1.95rem;
        font-weight: 700;
        color: #1C242F;
        margin-bottom: 2px;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-family: 'Inter', sans-serif;
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 20px;
    }

    /* Barra lateral estilo Catch Consulting */
    section[data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4 {
        font-family: 'Lexend', sans-serif !important;
        color: #1C242F !important;
        font-size: 0.88rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 10px;
    }

    /* Cajas ejecutivas de guía */
    .guide-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3AB0CD;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 20px;
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
    }

    .guide-title {
        font-family: 'Lexend', sans-serif;
        font-weight: 700;
        color: #1C242F;
        font-size: 1.02rem;
        margin-bottom: 8px;
    }

    /* Badges y etiquetas */
    .badge-pill {
        background-color: #E0F7FA;
        color: #0C8489;
        border: 1px solid #B2EBF2;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.82rem;
        letter-spacing: 0.02em;
        display: inline-block;
    }

    /* Tarjetas de Métricas (KPIs estilo Catch Consulting) */
    div[data-testid="stMetric"] {
        background: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
        border-top: 3px solid #3AB0CD !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08) !important;
    }

    div[data-testid="stMetricValue"] {
        font-family: 'Lexend', sans-serif !important;
        font-size: 1.55rem !important;
        font-weight: 700 !important;
        color: #1C242F !important;
    }

    div[data-testid="stMetricLabel"] {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        border-bottom: 2px solid #E2E8F0;
        margin-bottom: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 10px 18px;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        color: #64748B;
        border-radius: 6px 6px 0 0;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        color: #0C8489 !important;
        border-bottom: 2px solid #3AB0CD !important;
        background-color: transparent !important;
    }

    /* Botones de acción principales */
    div.stButton > button:first-child {
        background-color: #3AB0CD !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 9px 20px !important;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button:first-child:hover {
        background-color: #2CA0BD !important;
        box-shadow: 0 4px 8px rgba(58, 176, 205, 0.25) !important;
        color: #FFFFFF !important;
    }

    /* Botones de descarga */
    div.stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #1C242F !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 6px !important;
        padding: 9px 18px !important;
        transition: all 0.2s ease !important;
    }

    div.stDownloadButton > button:hover {
        border-color: #3AB0CD !important;
        color: #3AB0CD !important;
        background-color: #F8FAFC !important;
    }

    /* Alertas con tono corporativo */
    div[data-testid="stAlert"] {
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
    }

    div[data-testid="stAlert"][data-baseweb="notification"] {
        background-color: #F8FAFC !important;
        border-left: 4px solid #3AB0CD !important;
    }
</style>
""", unsafe_allow_html=True)

# Cargar datos consolidados
@st.cache_data
def load_datasets():
    df_long = pd.read_csv("data/master_catch_longitudinal.csv")
    df_bench = pd.read_csv("data/companies_benchmark.csv")
    return df_long, df_bench

df_long, df_bench = load_datasets()

# Inicializar motores
simulator = ReformSimulator(df_bench)
ai_advisor = CatchAIAdvisor(df_bench, df_long)

# BARRA LATERAL (Sidebar)
with st.sidebar:
    if svg_logo_raw:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; padding: 4px 0 16px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
            <div style="width: 44px; flex-shrink: 0;">{svg_logo_raw}</div>
            <div>
                <div style="font-family: 'Lexend', sans-serif; font-size: 1.25rem; font-weight: 700; color: #1C242F; line-height: 1.15;">
                    Catch <span style="color: #3AB0CD;">Consulting</span>
                </div>
                <div style="font-family: 'Inter', sans-serif; font-size: 0.72rem; color: #64748B; font-weight: 500; margin-top: 2px;">
                    Capital Humano & Cumplimiento
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.image("https://www.catchconsulting.com.mx/assets/iconos/logo-cc-moneda.png", width=180)
        
    st.markdown("### Reto Catch Consulting")
    st.markdown("**El Futuro de la Jornada Laboral en México**")
    st.divider()
    
    st.markdown("#### Filtros de Control")
    
    # Selector de Rol / Perfil
    perfil_usuario = st.selectbox(
        "Perfil / Rol de Usuario:",
        ["Dirección General", "Recursos Humanos (RH)", "Operaciones & Producción", "Nómina & Compensaciones"],
        key="sb_perfil"
    )
    
    # Selector de Empresa
    empresas_disponibles = ["Todas las Empresas (Visión Cluster)"] + sorted(list(df_bench['company'].unique()))
    empresa_seleccionada = st.selectbox("Empresa Seleccionada:", empresas_disponibles, key="sb_empresa")
    
    st.divider()
    st.markdown("#### Módulos de la Solución")
    modulo_activo = st.radio(
        "Navegación:",
        [
            "1. Resumen Ejecutivo & Benchmark",
            "2. Simulador de Reducción a 40 Horas",
            "3. Planificador Inteligente de Turnos",
            "4. Control de Horas Extra (LFT Dobles/Triples)",
            "5. Generador de Datos para SAP",
            "6. Asistente IA (Catch AI Advisor)"
        ],
        key="sb_modulo"
    )
    st.divider()
    st.caption("Solución desarrollada para el Concurso Catch Consulting. Cumplimiento LFT & Reforma 40h.")

# ENCABEZADO PRINCIPAL
col_title, col_badge = st.columns([4, 1])
with col_title:
    st.markdown('<p class="main-header">KRONOS CATCH <span style="font-weight: 300; color: #94A3B8;">|</span> <span style="color: #3AB0CD;">Workforce Planning & Compliance 40H</span></p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Vista analítica adaptada para: <b>{perfil_usuario}</b> &bull; Filtro activo: <b>{empresa_seleccionada}</b></p>', unsafe_allow_html=True)
with col_badge:
    st.markdown(f'<div style="text-align: right; padding-top: 15px;"><span class="badge-pill">{perfil_usuario.split()[0]} View</span></div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------------------------------
# MÓDULO 1: RESUMEN EJECUTIVO & BENCHMARK (DINÁMICO POR COMPAÑÍA Y POR PERFIL)
# -------------------------------------------------------------------------------------------------
if modulo_activo == "1. Resumen Ejecutivo & Benchmark":
    st.markdown(f"### Tablero de Control — Perfil: **{perfil_usuario}**")
    
    is_cluster = (empresa_seleccionada == "Todas las Empresas (Visión Cluster)")
    
    if is_cluster:
        st.write("Visualizando el **panorama agregado del cluster de 40 empresas** de Catch Consulting.")
    else:
        st.write(f"Visualizando métricas específicas y evolución longitudinal histórica de: **{empresa_seleccionada}**.")

    # 1. KPIs PERSONALIZADOS POR PERFIL
    if perfil_usuario == "Dirección General":
        k1, k2, k3, k4, k5 = st.columns(5)
        if is_cluster:
            k1.metric("Headcount Total", f"{int(df_bench['headcount_total'].sum()):,} personas")
            k2.metric("Índice IVR-40 Promedio", f"{df_bench['indice_vulnerabilidad_ivr40'].mean():.1f} / 100")
            k3.metric("Sobrecosto Anual 40h", f"${df_bench['sobrecosto_anual_nuevas_contrataciones'].sum()/1e6:.1f}M MXN")
            k4.metric("Déficit Semanal de Horas", f"{df_bench['brecha_horas_40h_planta_semanal'].sum():,.0f} hrs")
            k5.metric("Nuevos Puestos Req.", f"+{df_bench['headcount_requerido_40h'].sum():,.0f} ops")
        else:
            row_e = df_bench[df_bench['company'] == empresa_seleccionada].iloc[0]
            k1.metric("Headcount Total", f"{int(row_e['headcount_total']):,} personas")
            k2.metric("Índice IVR-40", f"{row_e['indice_vulnerabilidad_ivr40']:.0f} / 100", 
                      "Alto Riesgo" if row_e['indice_vulnerabilidad_ivr40'] >= 70 else "Moderado")
            k3.metric("Sobrecosto Anual 40h", f"${row_e['sobrecosto_anual_nuevas_contrataciones']/1e6:.2f}M MXN")
            k4.metric("Déficit Semanal", f"{row_e['brecha_horas_40h_planta_semanal']:,.1f} hrs")
            k5.metric("Nuevos Puestos Req.", f"+{row_e['headcount_requerido_40h']:.1f} ops")

    elif perfil_usuario == "Recursos Humanos (RH)":
        k1, k2, k3, k4, k5 = st.columns(5)
        if is_cluster:
            k1.metric("Headcount Operativo", f"{int(df_bench['headcount_operativo'].sum()):,} ops")
            k2.metric("Faltas Prom. Bimestral", f"{df_bench['faltas_tot_bimestre'].mean():,.0f} faltas")
            k3.metric("Rotación Vol. Mensual", f"{df_bench['pct_rotacion_op'].dropna().mean()*100:.2f}%")
            k4.metric("Empresas con 6 Días", f"{(df_bench['t1_dias'] == 'Lunes a Sábado').mean()*100:.1f}%")
            k5.metric("Ausentismo Injustificado", f"{df_bench['faltas_injust_op'].mean():,.0f} casos")
        else:
            row_e = df_bench[df_bench['company'] == empresa_seleccionada].iloc[0]
            k1.metric("Headcount Operativo", f"{int(row_e['headcount_operativo']):,} ops")
            k2.metric("Faltas Bimestrales", f"{row_e['faltas_tot_bimestre'] if pd.notna(row_e['faltas_tot_bimestre']) else 0:,.0f} faltas")
            k3.metric("Rotación Vol. Mensual", f"{row_e['pct_rotacion_op']*100 if pd.notna(row_e['pct_rotacion_op']) else 0:.2f}%")
            k4.metric("Días Trabajo Semanal", f"{row_e['t1_dias']}")
            k5.metric("Faltas Injustificadas", f"{row_e['faltas_injust_op'] if pd.notna(row_e['faltas_injust_op']) else 0:,.0f} casos")

    elif perfil_usuario == "Operaciones & Producción":
        k1, k2, k3, k4, k5 = st.columns(5)
        if is_cluster:
            k1.metric("Jornada de 12 Horas", f"{(df_bench['jornada_12h'] == 'Sí').mean()*100:.1f}% empresas")
            k2.metric("Rolado Semanal Turnos", f"{(df_bench['rolar_turnos'].str.contains('semana', na=False)).mean()*100:.1f}%")
            k3.metric("Comida en Jornada", f"{(df_bench['t1_comida'].str.contains('parte de la jornada', na=False)).mean()*100:.1f}%")
            k4.metric("Horas Semanales Actuales", f"{df_bench['horas_semanales_actuales'].mean():.1f} hrs/sem")
            k5.metric("Afectación Ausentismo", "Tiempo Extra (#1)")
        else:
            row_e = df_bench[df_bench['company'] == empresa_seleccionada].iloc[0]
            k1.metric("Jornada de 12 Horas", f"{row_e['jornada_12h']}")
            k2.metric("Rolado de Turnos", f"{row_e['rolar_turnos']}")
            k3.metric("Comida en Jornada", "Sí (Incluida)" if "parte" in str(row_e['t1_comida']) else "No (Extra)")
            k4.metric("Horas Semanales", f"{row_e['horas_semanales_actuales']:.1f} hrs/sem")
            k5.metric("Afectación Reportada", f"{str(row_e['afectacion_ausentismo'])[:20] or 'No reportada'}")

    elif perfil_usuario == "Nómina & Compensaciones":
        k1, k2, k3, k4, k5 = st.columns(5)
        if is_cluster:
            k1.metric("Salario Diario Inicial", f"${df_bench['salario_diario_inicial'].mean():.2f} MXN")
            k2.metric("Salario Diario Máximo", f"${df_bench['salario_diario_maximo'].mean():.2f} MXN")
            k3.metric("Costo Prom. Hora Normal", f"${df_bench['salario_hora_promedio'].mean():.2f} MXN")
            k4.metric("Costo Hora Extra Doble", f"${df_bench['costo_hora_extra_doble'].mean():.2f} MXN")
            k5.metric("Costo Hora Extra Triple", f"${df_bench['costo_hora_extra_triple'].mean():.2f} MXN")
        else:
            row_e = df_bench[df_bench['company'] == empresa_seleccionada].iloc[0]
            k1.metric("Salario Diario Inicial", f"${row_e['salario_diario_inicial']:.2f} MXN")
            k2.metric("Salario Diario Máximo", f"${row_e['salario_diario_maximo']:.2f} MXN")
            k3.metric("Costo Hora Normal", f"${row_e['salario_hora_promedio']:.2f} MXN")
            k4.metric("Costo Hora Doble (+100%)", f"${row_e['costo_hora_extra_doble']:.2f} MXN")
            k5.metric("Costo Hora Triple (+200%)", f"${row_e['costo_hora_extra_triple']:.2f} MXN")

    st.divider()

    # 2. GRÁFICAS REACTIVAS
    if is_cluster:
        st.markdown(f"#### Análisis Gráfico del Cluster — Enfoque: **{perfil_usuario}**")
        col_g1, col_g2 = st.columns(2)
        
        if perfil_usuario in ["Dirección General", "Operaciones & Producción"]:
            with col_g1:
                st.markdown("##### Días Laborables Semanales en Primer Turno")
                dias_counts = df_bench['t1_dias'].fillna("No especificado").value_counts().reset_index()
                dias_counts.columns = ['Esquema', 'Empresas']
                fig_dias = px.pie(
                    dias_counts, names='Esquema', values='Empresas', hole=0.45,
                    color_discrete_sequence=CATCH_PALETTE
                )
                fig_dias.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                apply_catch_theme(fig_dias)
                st.plotly_chart(fig_dias, use_container_width=True)
                
            with col_g2:
                st.markdown("##### Top 12 Empresas con Mayor Índice de Vulnerabilidad (IVR-40)")
                df_top_ivr = df_bench.sort_values(by='indice_vulnerabilidad_ivr40', ascending=False).head(12)
                fig_ivr = px.bar(
                    df_top_ivr, x='company', y='indice_vulnerabilidad_ivr40',
                    color='indice_vulnerabilidad_ivr40', color_continuous_scale='Reds'
                )
                fig_ivr.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300, showlegend=False)
                apply_catch_theme(fig_ivr)
                st.plotly_chart(fig_ivr, use_container_width=True)

        if perfil_usuario in ["Recursos Humanos (RH)", "Nómina & Compensaciones", "Dirección General"]:
            col_g3, col_g4 = st.columns(2)
            with col_g3:
                st.markdown("##### Curva Salarial Promedio por Categoría Operativa")
                sal_cats = pd.DataFrame({
                    'Nivel': ['1. Inicial (Capacitación)', '2. Intermedio-Bajo', '3. Intermedio-Alto', '4. Máximo (Multihabilidad)'],
                    'Salario Diario MXN': [
                        df_bench['salario_diario_inicial'].mean(),
                        df_bench['salario_diario_inter_bajo'].mean(),
                        df_bench['salario_diario_inter_alto'].mean(),
                        df_bench['salario_diario_maximo'].mean()
                    ]
                })
                fig_sal = px.bar(sal_cats, x='Nivel', y='Salario Diario MXN', text_auto='.2f', color='Salario Diario MXN', color_continuous_scale=['#E0F7FA', '#3AB0CD', '#0C8489', '#1C242F'])
                fig_sal.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300, showlegend=False)
                apply_catch_theme(fig_sal)
                st.plotly_chart(fig_sal, use_container_width=True)
                
            with col_g4:
                st.markdown("##### Correlación: Faltas Totales vs Plantilla Operativa")
                fig_scat = px.scatter(
                    df_bench, x='headcount_operativo', y='faltas_tot_bimestre',
                    hover_name='company', color='indice_vulnerabilidad_ivr40',
                    labels={'headcount_operativo': 'Headcount Operativo', 'faltas_tot_bimestre': 'Faltas Bimestre'},
                    color_continuous_scale=['#3AB0CD', '#F1A720', '#E92736']
                )
                fig_scat.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=300)
                apply_catch_theme(fig_scat)
                st.plotly_chart(fig_scat, use_container_width=True)
                
    else:
        # VISTA ESPECÍFICA DE LA EMPRESA SELECCIONADA
        st.markdown(f"#### Evolución Histórica Longitudinal y Comparativa: **{empresa_seleccionada}**")
        df_emp_hist = df_long[df_long['company'] == empresa_seleccionada].copy()
        
        # Ordenar periodos cronológicamente
        period_order = ['JUL-AGO_2024', 'SEP-OCT_2024', 'NOV-DIC_2024', 'ENE-FEB_2025', 'MAR-ABR_2025', 'MAY-JUN_2025', 'JUL-AGO_2025']
        df_emp_hist['period'] = pd.Categorical(df_emp_hist['period'], categories=period_order, ordered=True)
        df_emp_hist = df_emp_hist.sort_values('period')
        
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.markdown(f"##### Evolución de Plantilla Operativa ({len(df_emp_hist)} Bimestres)")
            fig_hc = px.line(
                df_emp_hist, x='period', y='headcount_operativo',
                markers=True, title=f"Headcount Operativo en {empresa_seleccionada}",
                line_shape='spline', color_discrete_sequence=['#3AB0CD']
            )
            fig_hc.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=300)
            apply_catch_theme(fig_hc)
            st.plotly_chart(fig_hc, use_container_width=True)

        with col_e2:
            st.markdown(f"##### Faltas y Ausentismo por Bimestre")
            fig_faltas = px.bar(
                df_emp_hist, x='period', y='faltas_tot_bimestre',
                title=f"Total Faltas Reportadas por Bimestre",
                text_auto=True, color_discrete_sequence=['#E92736']
            )
            fig_faltas.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=300)
            apply_catch_theme(fig_faltas)
            st.plotly_chart(fig_faltas, use_container_width=True)

        col_e3, col_e4 = st.columns(2)
        with col_e3:
            st.markdown(f"##### Comparativa Salarial: {empresa_seleccionada} vs Promedio Industria")
            row_cur = df_bench[df_bench['company'] == empresa_seleccionada].iloc[0]
            comp_sal = pd.DataFrame({
                'Categoría': ['Inicial', 'Intermedio-Bajo', 'Intermedio-Alto', 'Máximo'],
                'Esta Empresa': [
                    row_cur['salario_diario_inicial'], row_cur['salario_diario_inter_bajo'],
                    row_cur['salario_diario_inter_alto'], row_cur['salario_diario_maximo']
                ],
                'Promedio Industria': [
                    df_bench['salario_diario_inicial'].mean(), df_bench['salario_diario_inter_bajo'].mean(),
                    df_bench['salario_diario_inter_alto'].mean(), df_bench['salario_diario_maximo'].mean()
                ]
            })
            fig_comp = px.bar(comp_sal, x='Categoría', y=['Esta Empresa', 'Promedio Industria'], barmode='group', color_discrete_sequence=['#1C242F', '#3AB0CD'])
            fig_comp.update_layout(margin=dict(t=20, b=10, l=10, r=10), height=300)
            apply_catch_theme(fig_comp)
            st.plotly_chart(fig_comp, use_container_width=True)

        with col_e4:
            st.markdown(f"##### Brecha de Horas ante Reforma (48h a 40h)")
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=float(row_cur['brecha_horas_40h_planta_semanal']),
                title={'text': "Déficit Semanal de Horas en Planta", 'font': {'family': 'Inter', 'color': '#1C242F'}},
                gauge={
                    'axis': {'range': [0, max(5000, float(row_cur['brecha_horas_40h_planta_semanal']) * 1.3)]},
                    'bar': {'color': "#3AB0CD"},
                    'steps': [
                        {'range': [0, 1000], 'color': "#F0FDF4"},
                        {'range': [1000, 3000], 'color': "#FFFBEB"},
                        {'range': [3000, 10000], 'color': "#FEF2F2"}
                    ]
                }
            ))
            fig_gauge.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=300)
            apply_catch_theme(fig_gauge)
            st.plotly_chart(fig_gauge, use_container_width=True)

# -------------------------------------------------------------------------------------------------
# MÓDULO 2: SIMULADOR DE REDUCCIÓN A 40 HORAS
# -------------------------------------------------------------------------------------------------
elif modulo_activo == "2. Simulador de Reducción a 40 Horas":
    st.markdown("### Simulador Estratégico de Reducción de Jornada (48h a 40h)")
    
    # PANEL DE GUÍA EJECUTIVA NATIVO Y VISIBLE
    st.info("""
    ### Guía Ejecutiva: Simulador Estratégico de Reducción a 40 Horas
    * **1. Objetivo del Módulo:**  
      Modelo analítico y financiero diseñado para anticipar el impacto operativo de la reforma de reducción de jornada (48h a 40h semanales) en las empresas del cluster.
    * **2. Fundamento Metodológico:**  
      El déficit semanal de capacidad productiva se calcula como:  
      `Déficit Semanal = Headcount Operativo × (Horas Semanales Actuales − Horas Objetivo) × (1 − Ganancia Productividad)`.  
      Compara en tiempo real cuatro estrategias de adaptación: costos salariales, cargas IMSS/Infonavit y viabilidad jurídica frente a la LFT.
    * **3. Instrucciones de Uso:**  
      1° Selecciona la empresa a simular.  
      2° Modifica los parámetros de jornada meta, factor de prestaciones y porcentaje de recuperación en productividad.  
      3° Revisa la tabla y gráfico comparativo para evaluar la opción óptima en costo y riesgo normativo.
    """)
    
    col_s1, col_s2 = st.columns([1, 2])
    
    with col_s1:
        st.markdown("#### Parámetros de Simulación")
        def_idx = 0
        all_c = sorted(list(df_bench['company'].unique()))
        if empresa_seleccionada in all_c:
            def_idx = all_c.index(empresa_seleccionada)
            
        target_company = st.selectbox("Empresa a Simular:", all_c, index=def_idx, key="sim_target_comp")
        target_hours = st.slider("Jornada Semanal Objetivo (Horas):", min_value=36.0, max_value=48.0, value=40.0, step=1.0, key="sim_target_hours")
        prestaciones_pct = st.slider("Carga Prestaciones e IMSS (% sobre salario base):", min_value=20.0, max_value=45.0, value=30.0, step=1.0, key="sim_prestaciones") / 100.0
        ganancia_prod = st.slider("Ganancia Esperada en Productividad / Menor Fatiga (%):", min_value=0.0, max_value=15.0, value=5.0, step=1.0, key="sim_prod")
        costo_logistico = st.number_input("Costo Mensual Comedor & Transporte por Empleado (MXN):", value=1800.0, step=100.0, key="sim_logistica")
        
    with col_s2:
        res = simulator.simular_empresa(
            target_company,
            meta_horas_semanales=target_hours,
            factor_prestaciones=prestaciones_pct,
            costo_comedor_transporte_mensual=costo_logistico,
            mejora_productividad_pct=ganancia_prod
        )
        
        st.markdown(f"#### Resultados Proyectados: **{target_company}**")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Headcount Actual", f"{int(res['headcount_operativo'])} ops")
        with m2:
            st.metric("Brecha por Obrero", f"{res['brecha_horas_semanal_persona']:.1f} hrs/sem")
        with m3:
            st.metric("Déficit Total Planta", f"{res['brecha_total_planta_semanal']:,.0f} hrs/sem")
        with m4:
            st.metric("Salario por Hora", f"${res['salario_hora']:.2f} MXN")
            
        st.divider()
        st.markdown("#### Comparativa Estratégica de Costos y Riesgos")
        
        est = res['estrategias']
        est_df = pd.DataFrame([
            {
                "Estrategia Operativa": "1. Contratación Pura (100% Nuevos Puestos)",
                "Headcount Extra": f"+{est['100_NUEVAS_CONTRATACIONES']['headcount_adicional']:.1f} ops",
                "Costo Anual Proyectado": f"${est['100_NUEVAS_CONTRATACIONES']['costo_anual_mxn']:,.2f}",
                "Costo Mensual": f"${est['100_NUEVAS_CONTRATACIONES']['costo_mensual_mxn']:,.2f}",
                "Riesgo Legal / LFT": est['100_NUEVAS_CONTRATACIONES']['riesgo_legal']
            },
            {
                "Estrategia Operativa": "2. Cobertura con Tiempo Extra (100%)",
                "Headcount Extra": "0 ops",
                "Costo Anual Proyectado": f"${est['100_TIEMPO_EXTRA']['costo_anual_mxn']:,.2f}",
                "Costo Mensual": f"${est['100_TIEMPO_EXTRA']['costo_mensual_mxn']:,.2f}",
                "Riesgo Legal / LFT": est['100_TIEMPO_EXTRA']['riesgo_legal']
            },
            {
                "Estrategia Operativa": "3. Modelo Mixto Catch Consulting (Recomendado)",
                "Headcount Extra": f"+{est['MIXTA_RECOMENDADA_CATCH']['headcount_adicional']:.1f} ops",
                "Costo Anual Proyectado": f"${est['MIXTA_RECOMENDADA_CATCH']['costo_anual_mxn']:,.2f}",
                "Costo Mensual": f"${est['MIXTA_RECOMENDADA_CATCH']['costo_mensual_mxn']:,.2f}",
                "Riesgo Legal / LFT": est['MIXTA_RECOMENDADA_CATCH']['riesgo_legal']
            },
            {
                "Estrategia Operativa": "4. Turno Comprimido 4x3 (10h)",
                "Headcount Extra": f"+{est['COMPRIMIDA_4X3_10H']['headcount_adicional']:.1f} ops",
                "Costo Anual Proyectado": f"${est['COMPRIMIDA_4X3_10H']['costo_anual_mxn']:,.2f}",
                "Costo Mensual": f"${est['COMPRIMIDA_4X3_10H']['costo_mensual_mxn']:,.2f}",
                "Riesgo Legal / LFT": "Excelente cumplimiento (3 días descanso)"
            }
        ])
        st.dataframe(est_df, use_container_width=True, hide_index=True)
        
        # Gráfico comparativo de costos
        costos_plot = pd.DataFrame({
            "Estrategia": ["100% Contratar", "100% Tiempo Extra", "Modelo Mixto Catch (Recomendado)", "Turno 4x3 (10h)"],
            "Costo Anual MXN": [
                est['100_NUEVAS_CONTRATACIONES']['costo_anual_mxn'],
                est['100_TIEMPO_EXTRA']['costo_anual_mxn'],
                est['MIXTA_RECOMENDADA_CATCH']['costo_anual_mxn'],
                est['COMPRIMIDA_4X3_10H']['costo_anual_mxn']
            ]
        })
        fig_cost = px.bar(
            costos_plot, x='Estrategia', y='Costo Anual MXN',
            color='Estrategia', text_auto=',.0f',
            color_discrete_sequence=['#3AB0CD', '#E92736', '#0C8489', '#64748B']
        )
        fig_cost.update_layout(height=260, margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
        apply_catch_theme(fig_cost)
        st.plotly_chart(fig_cost, use_container_width=True)

# -------------------------------------------------------------------------------------------------
# MÓDULO 3: PLANIFICADOR INTELIGENTE DE TURNOS
# -------------------------------------------------------------------------------------------------
elif modulo_activo == "3. Planificador Inteligente de Turnos":
    st.markdown("### Programador Inteligente de Turnos y Cuadrillas")
    
    # PANEL DE GUÍA EJECUTIVA NATIVO Y VISIBLE
    st.info("""
    ### Guía Ejecutiva: Planificador Inteligente de Turnos y Cuadrillas
    * **1. Objetivo del Módulo:**  
      Estructura los horarios explícitos de trabajo (horas de entrada, salida y comida) para cuadrillas de producción, asegurando el cumplimiento de la Ley Federal del Trabajo (LFT) y la reforma de 40 horas.
    * **2. Cuadrilla o Línea de Producción:**  
      Representa una célula de trabajo (ensamble, soldadura, maquinado CNC, pintura, almacén) con operadores compartiendo el mismo turno y horario de planta.
    * **3. Algoritmo de Cálculo:**  
      Genera horas exactas de entrada y salida, programa la ventana de comida a mitad de jornada y aplica el régimen de descansos semanales (1 día según LFT actual vs 2 días obligatorios en la reforma). Produce el rol nominal detallado de cada colaborador listo para exportación.
    * **4. Instrucciones de Uso:**  
      1° Define el nombre de la cuadrilla y la plantilla de operadores.  
      2° Elige la hora oficial de entrada, tipo de turno y duración de la comida.  
      3° Selecciona el esquema de descanso semanal (1 día actual vs 2 días reforma 40h).  
      4° Haz clic en **'Generar Horario de Trabajo'** para auditar el cumplimiento normativo y descargar el cronograma en CSV.
    """)
    
    col_p1, col_p2 = st.columns([1, 2])
    
    with col_p1:
        st.markdown("#### Configuración del Turno y Cuadrilla")
        with st.form("form_cuadrilla"):
            opciones_cuadrilla = [
                "Línea de Ensamble A1", "Celda de Soldadura y Chasis", "Área de Maquinado CNC",
                "Línea de Pintura Automotriz", "Cuadrilla de Empaque y Logística", "Personalizar nombre..."
            ]
            tipo_seleccionado = st.selectbox("Línea / Cuadrilla de Producción:", opciones_cuadrilla, key="sel_cuadrilla")
            
            if tipo_seleccionado == "Personalizar nombre...":
                nombre_cuadrilla = st.text_input("Escribe el nombre de tu Cuadrilla:", value="Mi Cuadrilla Especial", key="txt_cuadrilla_custom")
            else:
                nombre_cuadrilla = tipo_seleccionado
                
            tamano_cuadrilla = st.slider("Cantidad de Operadores en esta Línea:", 5, 150, 25, key="sld_tamano_cuadrilla")
            
            tipo_turno = st.selectbox(
                "Tipo de Turno Base:",
                ["Diurno (8 hrs)", "Mixto (7.5 hrs)", "Nocturno (7 hrs)", "Comprimido 4x3 (10 hrs)", "Especial (12 hrs)"],
                key="sel_tipo_turno"
            )
            
            hora_entrada_sel = st.selectbox(
                "Hora de Entrada Oficial:",
                ["06:00", "07:00", "08:00", "08:30", "14:00", "15:00", "16:00", "22:00", "23:00"],
                index=1,
                key="sel_hora_entrada"
            )
            
            minutos_comida = st.selectbox("Tiempo de Comedor / Descanso:", [30, 45, 60], index=0, key="sel_min_comida")
            incluye_comida = st.checkbox("Tiempo de comida pagado dentro de la jornada", value=True, key="chk_comida")
            
            esquema_descanso = st.radio("Régimen de Descanso Semanal:", ["1 Día (LFT Actual)", "2 Días (Reforma 40h)"], key="rad_descanso")
            
            btn_actualizar = st.form_submit_button("Generar Horario de Trabajo")
        
    with col_p2:
        st.markdown(f"#### Horario Semanal Programado: **{nombre_cuadrilla}**")
        
        # Parseo de horas y duraciones
        h_diarias = 8.0 if "8" in tipo_turno else 7.5 if "7.5" in tipo_turno else 7.0 if "7" in tipo_turno else 10.0 if "10" in tipo_turno else 12.0
        
        # Cálculo de hora de entrada, comida y salida
        h_ent_h, h_ent_m = map(int, hora_entrada_sel.split(":"))
        ent_dt = datetime.datetime(2026, 10, 19, h_ent_h, h_ent_m)
        
        # Comida a mitad de jornada
        mitad_minutos = int((h_diarias / 2.0) * 60)
        comida_inicio_dt = ent_dt + datetime.timedelta(minutes=mitad_minutos)
        comida_fin_dt = comida_inicio_dt + datetime.timedelta(minutes=minutos_comida)
        
        # Salida
        if incluye_comida:
            salida_dt = ent_dt + datetime.timedelta(minutes=int(h_diarias * 60))
            h_efectivas_dia = h_diarias - (minutos_comida / 60.0)
        else:
            salida_dt = ent_dt + datetime.timedelta(minutes=int(h_diarias * 60) + minutos_comida)
            h_efectivas_dia = h_diarias
            
        str_entrada = ent_dt.strftime("%H:%M hrs")
        str_comida = f"{comida_inicio_dt.strftime('%H:%M')} a {comida_fin_dt.strftime('%H:%M')} ({minutos_comida} min)"
        str_salida = salida_dt.strftime("%H:%M hrs")
        
        dias_sem = [
            ("Lunes", "19/10/2026"), ("Martes", "20/10/2026"), ("Miércoles", "21/10/2026"),
            ("Jueves", "22/10/2026"), ("Viernes", "23/10/2026"), ("Sábado", "24/10/2026"), ("Domingo", "25/10/2026")
        ]
        
        programacion = []
        for d, fecha in dias_sem:
            if esquema_descanso == "2 Días (Reforma 40h)":
                if h_diarias == 10.0:
                    is_work = (d not in ["Viernes", "Sábado", "Domingo"])
                else:
                    is_work = (d not in ["Sábado", "Domingo"])
            else:
                if h_diarias == 12.0:
                    is_work = (d in ["Lunes", "Martes", "Miércoles", "Jueves"])
                else:
                    is_work = (d != "Domingo")
                
            programacion.append({
                "Día": d,
                "Fecha": fecha,
                "Estatus": "Laborable" if is_work else "Descanso Semanal Obligatorio",
                "Hora Entrada": str_entrada if is_work else "---",
                "Ventana Comedor": str_comida if is_work else "---",
                "Hora Salida": str_salida if is_work else "---",
                "Horas Presenciales": f"{h_diarias:.1f} hrs" if is_work else "0.0 hrs",
                "Horas Efectivas Producción": f"{h_efectivas_dia:.1f} hrs" if is_work else "0.0 hrs",
                "Régimen LFT": tipo_turno.split()[0] if is_work else "Descanso Legal"
            })
            
        prog_df = pd.DataFrame(programacion)
        st.dataframe(prog_df, use_container_width=True, hide_index=True)
        
        # Métricas de resumen
        total_dias_lab = sum(1 for p in programacion if "Laborable" in p["Estatus"])
        total_horas_sem = total_dias_lab * h_diarias
        total_horas_efectivas_cuadrilla = total_dias_lab * h_efectivas_dia * tamano_cuadrilla
        
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            st.metric("Horas Semanales por Persona", f"{total_horas_sem:.1f} hrs", f"{total_dias_lab} días laborables")
        with cp2:
            st.metric("Horas Efectivas Cuadrilla", f"{total_horas_efectivas_cuadrilla:,.0f} hrs/sem", f"{tamano_cuadrilla} operadores")
        with cp3:
            cumple_40 = (total_horas_sem <= 40.0)
            st.metric("Semáforo LFT 40h", "Cumple Regla 40h" if cumple_40 else f"Excede por {total_horas_sem - 40:.1f}h")
            
        st.divider()
        st.markdown("#### Exportar Horario Oficial de Trabajo")
        
        # Generar Rol Nominal detallado para cada operador de la cuadrilla
        rol_nominal = []
        for op_idx in range(1, tamano_cuadrilla + 1):
            pernr_op = f"OP-{op_idx:03d}"
            nombre_op = f"Operador {op_idx:02d} ({nombre_cuadrilla})"
            for p in programacion:
                rol_nominal.append({
                    "ID_Operador": pernr_op,
                    "Nombre_Colaborador": nombre_op,
                    "Cuadrilla": nombre_cuadrilla,
                    "Tipo_Turno": tipo_turno,
                    "Día": p["Día"],
                    "Fecha": p["Fecha"],
                    "Estatus": p["Estatus"],
                    "Hora_Entrada": p["Hora Entrada"],
                    "Ventana_Comedor": p["Ventana Comedor"],
                    "Hora_Salida": p["Hora Salida"],
                    "Horas_Programadas": p["Horas Presenciales"],
                    "Horas_Efectivas": p["Horas Efectivas Producción"]
                })
        df_rol_nominal = pd.DataFrame(rol_nominal)
        
        csv_horario_semanal = prog_df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        csv_rol_nominal = df_rol_nominal.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "Descargar Horario Semanal Oficial (CSV)",
                data=csv_horario_semanal,
                file_name=f"Horario_Semanal_{nombre_cuadrilla.replace(' ', '_')}.csv",
                mime="text/csv",
                key="dl_horario_sem"
            )
        with col_dl2:
            st.download_button(
                f"Descargar Rol Nominal ({tamano_cuadrilla} Operadores)",
                data=csv_rol_nominal,
                file_name=f"Rol_Nominal_{nombre_cuadrilla.replace(' ', '_')}.csv",
                mime="text/csv",
                key="dl_rol_nominal"
            )

# -------------------------------------------------------------------------------------------------
# MÓDULO 4: CONTROL DE HORAS EXTRA (LFT DOBLES Y TRIPLES)
# -------------------------------------------------------------------------------------------------
elif modulo_activo == "4. Control de Horas Extra (LFT Dobles/Triples)":
    st.markdown("### Validador y Liquidador de Horas Extras (LFT)")
    
    # PANEL DE GUÍA EJECUTIVA NATIVO Y VISIBLE
    st.info("""
    ### Guía Ejecutiva: Validador y Liquidador de Horas Extras (LFT)
    * **1. Objetivo del Módulo:**  
      Audita las horas extraordinarias trabajadas conforme a los **Artículos 66, 67 y 68 de la Ley Federal del Trabajo (LFT)**.
    * **2. Regla Legal 3x3 de la LFT:**  
      • **Horas Dobles (+100% de recargo):** La ley autoriza un máximo de **3 horas extras por día y hasta 3 veces por semana** (máximo 9 horas semanales).  
      • **Horas Triples (+200% de recargo):** Cuando se exceden 3 horas en un solo día, se labora tiempo extra un **4to día en la misma semana**, o se superan las 9 horas semanales acumuladas, todas las horas adicionales se liquidan al triple (+200%).  
      • **Régimen Sancionatorio STPS:** La STPS sanciona el exceso de jornada con multas de 50 a 5,000 UMAs (**$5,657 a $565,700 MXN**) según el Art. 994 Fracc. I de la LFT.
    * **3. Instrucciones de Uso:**  
      1° Captura el salario diario del colaborador y su tipo de jornada ordinaria.  
      2° Ingresa las horas extras trabajadas de Lunes a Domingo.  
      3° Haz clic en **'Calcular Liquidación y Auditar LFT'** para obtener el desglose en pesos y la auditoría de riesgos de inspección.
    """)
    
    col_e1, col_e2 = st.columns([1, 1])
    
    with col_e1:
        st.markdown("#### Captura de Tiempo Extra Semanal")
        with st.form("form_horas_extra"):
            salario_colab = st.number_input("Salario Diario del Colaborador (MXN):", value=450.0, step=20.0, key="f_sal_colab")
            tipo_j = st.selectbox("Tipo de Jornada Ordinaria:", ["DIURNA", "MIXTA", "NOCTURNA"], key="f_tipo_j")
            
            st.write("Horas extraordinarias laboradas en la semana:")
            c_d1, c_d2 = st.columns(2)
            with c_d1:
                he_lunes = st.number_input("Lunes (hrs extra):", min_value=0.0, max_value=12.0, value=2.0, step=0.5, key="f_he_lun")
                he_martes = st.number_input("Martes (hrs extra):", min_value=0.0, max_value=12.0, value=3.0, step=0.5, key="f_he_mar")
                he_miercoles = st.number_input("Miércoles (hrs extra):", min_value=0.0, max_value=12.0, value=2.0, step=0.5, key="f_he_mie")
                he_jueves = st.number_input("Jueves (hrs extra):", min_value=0.0, max_value=12.0, value=3.0, step=0.5, key="f_he_jue")
            with c_d2:
                he_viernes = st.number_input("Viernes (hrs extra):", min_value=0.0, max_value=12.0, value=2.0, step=0.5, key="f_he_vie")
                he_sabado = st.number_input("Sábado (hrs extra):", min_value=0.0, max_value=12.0, value=0.0, step=0.5, key="f_he_sab")
                he_domingo = st.number_input("Domingo (hrs extra):", min_value=0.0, max_value=12.0, value=0.0, step=0.5, key="f_he_dom")
                
            btn_calc = st.form_submit_button("Calcular Liquidación y Auditar LFT")

    with col_e2:
        horas_semana = [he_lunes, he_martes, he_miercoles, he_jueves, he_viernes, he_sabado, he_domingo]
        calc = LFTRulesEngine.calcular_horas_extra(horas_semana, salario_colab, tipo_j)
        
        st.markdown("#### Liquidación y Cumplimiento Normativo")
        
        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("Total Horas Extra", f"{calc['total_horas_extra']:.1f} hrs")
        with k2:
            st.metric("Horas Dobles (100%)", f"{calc['horas_dobles']:.1f} hrs", f"${calc['monto_dobles_mxn']:.2f}")
        with k3:
            st.metric("Horas Triples (200%)", f"{calc['horas_triples']:.1f} hrs", f"${calc['monto_triples_mxn']:.2f}", delta_color="inverse")
            
        st.metric("Importe Total a Pagar en Nómina", f"${calc['monto_total_extra_mxn']:,.2f} MXN")
        st.divider()
        
        if calc['tiene_infracciones']:
            st.error("Alerta de Riesgo Legal STPS (Infracciones Detectadas):")
            for inf in calc['infracciones_detectadas']:
                st.write(f"• {inf}")
            st.warning(f"Riesgo de sanción administrativa por la STPS (Art. 994 Fracc. I LFT): entre **${calc['multa_estimada_stps']['min_mxn']:,.2f}** y **${calc['multa_estimada_stps']['max_mxn']:,.2f} MXN**.")
        else:
            st.success("Cumplimiento Óptimo: Las horas extras reportadas se encuentran dentro de los límites legales de la LFT (máx 3h/día, máx 3 días y máx 9h dobles).")

# -------------------------------------------------------------------------------------------------
# MÓDULO 5: GENERADOR DE DATOS PARA SAP (CON DICCIONARIO COMPLETO DE CAMPOS)
# -------------------------------------------------------------------------------------------------
elif modulo_activo == "5. Generador de Datos para SAP":
    st.markdown("### Módulo de Interfaz & Exportación para SAP HCM / SuccessFactors")
    st.write("Genera archivos listos para carga masiva directa en SAP (LSMW / LTMC / Batch Input), eliminando el retrabajo manual en Excel y asegurando total consistencia con Nómina.")
    
    # GUÍA GENERAL DEL MÓDULO SAP
    st.markdown("""
    <div class="guide-box">
        <div class="guide-title">Integración Técnica con SAP HCM / SuccessFactors</div>
        <p style="margin-bottom: 6px;">En SAP HCM, los datos de los trabajadores se almacenan en estructuras denominadas <b>Infotipos (IT)</b> de cuatro dígitos. Para la gestión integral del tiempo y nómina, la plataforma produce automáticamente los tres infotipos oficiales:</p>
        <p style="margin-bottom: 0px;">
        • <b>Infotipo 2005 (Horas Extras):</b> Transfiere las horas dobles y triples calculadas con sus respectivos importes en pesos para pago en nómina.<br>
        • <b>Infotipo 2001 (Ausencias):</b> Registra faltas, incapacidades del IMSS y vacaciones devengadas para control de ausentismo.<br>
        • <b>Infotipo 2002 (Presencias):</b> Define la jornada asignada (8h, 7.5h, 7h, 10h o 12h) para cada trabajador de la planta.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    tab_2005, tab_2001, tab_2002, tab_diccionario = st.tabs([
        "Horas Extras (Infotipo 2005)",
        "Ausencias & Incapacidades (Infotipo 2001)",
        "Turnos Planificados (Infotipo 2002)",
        "Diccionario de Campos SAP HCM"
    ])
    
    with tab_2005:
        st.markdown("#### Layout SAP Infotipo 2005 - Horas Extraordinarias (Overtime)")
        st.caption("Estructura enviada al módulo de Nómina (PY) de SAP con separación automática de horas dobles y triples.")
        sample_he = []
        for i in range(1, 16):
            pernr = f"000100{i:02d}"
            h_dobles = float(np.random.choice([2, 4, 6, 8]))
            h_triples = float(np.random.choice([0, 0, 2, 4]))
            sal_h = 55.0
            
            sample_he.append({
                "pernr": pernr,
                "subty": "1010",
                "begda": datetime.date.today().strftime("%Y%m%d"),
                "endda": datetime.date.today().strftime("%Y%m%d"),
                "anzhl": h_dobles,
                "betrg": h_dobles * sal_h * 2.0
            })
            if h_triples > 0:
                sample_he.append({
                    "pernr": pernr,
                    "subty": "1020",
                    "begda": datetime.date.today().strftime("%Y%m%d"),
                    "endda": datetime.date.today().strftime("%Y%m%d"),
                    "anzhl": h_triples,
                    "betrg": h_triples * sal_h * 3.0
                })
                
        df_sap_2005 = SAPHCMExporter.generar_infotipo_2005(sample_he)
        st.dataframe(df_sap_2005, use_container_width=True)
        
        csv_2005 = df_sap_2005.to_csv(index=False).encode('utf-8')
        txt_2005 = SAPHCMExporter.exportar_layout_plano_sap(df_sap_2005, "2005").encode('utf-8')
        
        c_d1, c_d2 = st.columns(2)
        with c_d1:
            st.download_button("Descargar CSV Infotipo 2005", data=csv_2005, file_name="SAP_IT2005_HorasExtras.csv", mime="text/csv", key="dl_csv_2005")
        with c_d2:
            st.download_button("Descargar TXT Batch Input SAP 2005", data=txt_2005, file_name="SAP_IT2005_BatchInput.txt", mime="text/plain", key="dl_txt_2005")

    with tab_2001:
        st.markdown("#### Layout SAP Infotipo 2001 - Ausentismos, Incapacidades & Vacaciones")
        sample_aus = [
            {"pernr": "00010001", "subty": "0300", "stdaz": 8.0, "motivo": "Falta Injustificada"},
            {"pernr": "00010002", "subty": "0100", "stdaz": 8.0, "motivo": "Enfermedad General (IMSS)"},
            {"pernr": "00010003", "subty": "0200", "stdaz": 8.0, "motivo": "Riesgo de Trabajo"},
            {"pernr": "00010004", "subty": "0400", "stdaz": 8.0, "motivo": "Vacaciones Dignas LFT"}
        ]
        df_sap_2001 = SAPHCMExporter.generar_infotipo_2001(sample_aus)
        st.dataframe(df_sap_2001, use_container_width=True)
        csv_2001 = df_sap_2001.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV Infotipo 2001", data=csv_2001, file_name="SAP_IT2001_Ausencias.csv", mime="text/csv", key="dl_csv_2001")

    with tab_2002:
        st.markdown("#### Layout SAP Infotipo 2002 - Presencias y Turnos Planificados")
        sample_turnos = [
            {"pernr": "00010001", "subty": "0800", "stdaz": 8.0, "tprog": "D08", "descripcion": "Turno 1 Diurno 8h"},
            {"pernr": "00010002", "subty": "0810", "stdaz": 12.0, "tprog": "T12", "descripcion": "Jornada Operativa 12h 4x3"},
            {"pernr": "00010003", "subty": "0820", "stdaz": 7.0, "tprog": "N07", "descripcion": "Turno 3 Nocturno 7h"}
        ]
        df_sap_2002 = SAPHCMExporter.generar_infotipo_2002(sample_turnos)
        st.dataframe(df_sap_2002, use_container_width=True)
        csv_2002 = df_sap_2002.to_csv(index=False).encode('utf-8')
        st.download_button("Descargar CSV Infotipo 2002", data=csv_2002, file_name="SAP_IT2002_Presencias.csv", mime="text/csv", key="dl_csv_2002")

    with tab_diccionario:
        st.markdown("#### Diccionario de Datos: Estructura Oficial de Campos en SAP HCM")
        
        st.markdown("##### 1. Columnas de Infotipo 2005 (Horas Extras):")
        dict_2005 = pd.DataFrame([
            {"Columna": "PERNR", "Nombre en SAP": "Personal Number", "Tipo": "Numérico (8)", "Descripción": "Identificador o matrícula única del trabajador en SAP", "Valores Posibles / Ejemplo": "Ej. '00010001'"},
            {"Columna": "INFTY", "Nombre en SAP": "Infotype", "Tipo": "Texto (4)", "Descripción": "Clave que indica el tipo de registro maestro en SAP", "Valores Posibles / Ejemplo": "'2005' (Horas Extraordinarias)"},
            {"Columna": "SUBTY", "Nombre en SAP": "Subtype", "Tipo": "Texto (4)", "Descripción": "Categoría legal de la hora extra", "Valores Posibles / Ejemplo": "'1010' = Horas Dobles (100% recargo), '1020' = Horas Triples (200% recargo)"},
            {"Columna": "BEGDA", "Nombre en SAP": "Begin Date", "Tipo": "Fecha (8)", "Descripción": "Fecha en que se devengó la hora extraordinaria (formato YYYYMMDD)", "Valores Posibles / Ejemplo": "Ej. '20261019'"},
            {"Columna": "ENDDA", "Nombre en SAP": "End Date", "Tipo": "Fecha (8)", "Descripción": "Fecha de cierre del devengo", "Valores Posibles / Ejemplo": "Ej. '20261019'"},
            {"Columna": "LGART", "Nombre en SAP": "Lohnart (Wage Type)", "Tipo": "Texto (4)", "Descripción": "Concepto de nómina (CC-Nómina) que se liquidará en el cálculo salarial", "Valores Posibles / Ejemplo": "'HEDO' (Horas Extra Dobles) o 'HETR' (Horas Extra Triples)"},
            {"Columna": "ANZHL", "Nombre en SAP": "Number / Hours", "Tipo": "Decimal", "Descripción": "Cantidad exacta de horas extraordinarias a pagar", "Valores Posibles / Ejemplo": "Ej. '6.00'"},
            {"Columna": "BETRG", "Nombre en SAP": "Amount / Betrag", "Tipo": "Moneda", "Descripción": "Importe en pesos a pagar ya calculado con su recargo de ley", "Valores Posibles / Ejemplo": "Ej. '660.00'"},
            {"Columna": "WAERS", "Nombre en SAP": "Currency Key", "Tipo": "Texto (3)", "Descripción": "Moneda de liquidación", "Valores Posibles / Ejemplo": "'MXN' (Pesos Mexicanos)"}
        ])
        st.dataframe(dict_2005, use_container_width=True, hide_index=True)

        st.markdown("##### 2. Columnas de Infotipo 2001 (Ausencias e Incapacidades):")
        dict_2001 = pd.DataFrame([
            {"Columna": "PERNR", "Nombre en SAP": "Personal Number", "Tipo": "Numérico (8)", "Descripción": "Matrícula del empleado", "Valores Posibles / Ejemplo": "Ej. '00010001'"},
            {"Columna": "INFTY", "Nombre en SAP": "Infotype", "Tipo": "Texto (4)", "Descripción": "Clave de infotipo", "Valores Posibles / Ejemplo": "'2001' (Ausentismos)"},
            {"Columna": "SUBTY", "Nombre en SAP": "Absence Subtype", "Tipo": "Texto (4)", "Descripción": "Tipo de evento de ausencia", "Valores Posibles / Ejemplo": "'0100' (Enfermedad IMSS), '0200' (Riesgo Trabajo), '0300' (Falta Injustificada), '0400' (Vacaciones)"},
            {"Columna": "BEGDA / ENDDA", "Nombre en SAP": "Date Range", "Tipo": "Fecha (8)", "Descripción": "Periodo que duró la ausencia", "Valores Posibles / Ejemplo": "Formato 'AAAAMMDD'"},
            {"Columna": "STDAZ", "Nombre en SAP": "Hours of Absence", "Tipo": "Decimal", "Descripción": "Horas ausentes de la jornada pactada", "Valores Posibles / Ejemplo": "Ej. '8.00'"},
            {"Columna": "MOTIVO", "Nombre en SAP": "Description", "Tipo": "Texto", "Descripción": "Descripción legible de la causa de falta", "Valores Posibles / Ejemplo": "Ej. 'Falta Injustificada', 'Incapacidad RT'"},
            {"Columna": "SPRPS", "Nombre en SAP": "Lock Indicator", "Tipo": "Texto (1)", "Descripción": "Bandera de bloqueo para revisión de nómina", "Valores Posibles / Ejemplo": "'' (Vacío = Aprobado), 'X' (En revisión)"}
        ])
        st.dataframe(dict_2001, use_container_width=True, hide_index=True)

        st.markdown("##### 3. Columnas de Infotipo 2002 (Presencias y Turnos Asignados):")
        dict_2002 = pd.DataFrame([
            {"Columna": "PERNR", "Nombre en SAP": "Personal Number", "Tipo": "Numérico (8)", "Descripción": "Matrícula del empleado", "Valores Posibles / Ejemplo": "Ej. '00010001'"},
            {"Columna": "INFTY", "Nombre en SAP": "Infotype", "Tipo": "Texto (4)", "Descripción": "Clave de infotipo", "Valores Posibles / Ejemplo": "'2002' (Presencias)"},
            {"Columna": "SUBTY", "Nombre en SAP": "Presence Subtype", "Tipo": "Texto (4)", "Descripción": "Tipo de jornada programada", "Valores Posibles / Ejemplo": "'0800' (Jornada Ordinaria), '0810' (Turno Especial 12h)"},
            {"Columna": "STDAZ", "Nombre en SAP": "Daily Hours", "Tipo": "Decimal", "Descripción": "Horas diarias asignadas al turno", "Valores Posibles / Ejemplo": "8.00, 7.50, 7.00, 10.00 o 12.00"},
            {"Columna": "TPROG", "Nombre en SAP": "Daily Work Schedule", "Tipo": "Texto (4)", "Descripción": "Clave del programa diario de tiempos en SAP", "Valores Posibles / Ejemplo": "'D08' (Diurno 8h), 'N07' (Nocturno 7h), 'M75' (Mixto 7.5h), 'T12' (12h)"},
            {"Columna": "TURNO_DESCRIP", "Nombre en SAP": "Text Description", "Tipo": "Texto", "Descripción": "Nombre del rol de turno para la operación", "Valores Posibles / Ejemplo": "Ej. 'Turno 1 Diurno 8h'"}
        ])
        st.dataframe(dict_2002, use_container_width=True, hide_index=True)

# -------------------------------------------------------------------------------------------------
# MÓDULO 6: ASISTENTE DE IA (CATCH AI ADVISOR)
# -------------------------------------------------------------------------------------------------
elif modulo_activo == "6. Asistente IA (Catch AI Advisor)":
    st.markdown("### Catch AI Advisor | Consultor Analítico de Capital Humano")
    st.write("Realiza consultas sobre benchmarking de empresas, marco legal LFT, costos de reforma a 40h o liquidación de horas extra.")
    
    st.markdown("**Consultas Rápidas Sugeridas:**")
    qp_col1, qp_col2, qp_col3 = st.columns(3)
    prompt_in = None
    with qp_col1:
        if st.button("Radiografía de Compañía 1", key="btn_qp1"):
            prompt_in = "Dime la radiografía completa de la Compañía 1"
    with qp_col2:
        if st.button("Impacto Global de la Reforma 40h", key="btn_qp2"):
            prompt_in = "Cuál es el impacto global si todo el cluster reduce la jornada a 40 horas?"
    with qp_col3:
        if st.button("Reglas de Horas Extra Dobles/Triples", key="btn_qp3"):
            prompt_in = "Cómo se calculan legalmente las horas extra dobles y triples en la LFT?"
            
    user_query = st.text_input("Escribe tu pregunta para el Asistente de IA:", value=prompt_in or "", placeholder="Ej: ¿Cómo afecta el ausentismo a las horas extras? o ¿Cuál es el diagnóstico de Compañía 20?", key="txt_ai_query")
    
    if user_query:
        with st.spinner("Catch AI Advisor analizando la base histórica y la legislación laboral..."):
            ans = ai_advisor.responder_consulta(user_query)
            st.markdown(ans["respuesta"])
            st.divider()
            st.caption("Respuesta generada en tiempo real con base en datos de BASE HISTORICA.xlsx y la Ley Federal del Trabajo.")
    else:
        st.info("Selecciona una consulta rápida arriba o escribe cualquier pregunta en el cuadro de texto para obtener asesoría instantánea.")
