"""
Módulo de Simulación de Reducción de Jornada Laboral (48h a 40h en México)
Permite modelar escenarios de transición, brecha de headcount, impacto presupuestal
y comparativa de estrategias operativas para Catch Consulting.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np

class ReformSimulator:
    """Motor de simulación de impacto de la reforma de 40 horas semanales."""
    
    def __init__(self, df_companies: pd.DataFrame):
        self.df = df_companies.copy()
        
    def simular_empresa(
        self,
        company_name: str,
        meta_horas_semanales: float = 40.0,
        estrategia: str = "MIXTA",  # 'CONTRATAR', 'TIEMPO_EXTRA', 'MIXTA', 'COMPRIMIDA_4X3'
        factor_prestaciones: float = 0.30,  # 30% adicional a salario base (IMSS, Infonavit, previsión social)
        costo_comedor_transporte_mensual: float = 1800.0,  # Costo por colaborador adicional
        mejora_productividad_pct: float = 5.0  # % de productividad que se espera recuperar por menor fatiga
    ) -> Dict[str, Any]:
        """Calcula el impacto detallado para una empresa específica."""
        emp = self.df[self.df['company'] == company_name]
        if emp.empty:
            # Tomar promedio si no existe
            row = self.df.mean(numeric_only=True)
            headcount_op = float(row.get('headcount_operativo', 500))
            salario_diario = float(row.get('salario_diario_promedio', 400))
            horas_actuales = 48.0
        else:
            row = emp.iloc[0]
            headcount_op = float(row['headcount_operativo']) if pd.notna(row['headcount_operativo']) else 500.0
            salario_diario = float(row['salario_diario_promedio']) if pd.notna(row['salario_diario_promedio']) else 400.0
            horas_actuales = float(row['horas_semanales_actuales']) if pd.notna(row['horas_semanales_actuales']) else 48.0
            
        salario_hora = salario_diario / 8.0
        brecha_horas_persona = max(0.0, horas_actuales - meta_horas_semanales)
        
        # Reducción de brecha por efecto de ganancia en productividad (menor fatiga / NOM-035)
        horas_efectivas_a_cubrir_persona = brecha_horas_persona * (1.0 - (mejora_productividad_pct / 100.0))
        
        brecha_total_planta_semanal = horas_efectivas_a_cubrir_persona * headcount_op
        brecha_total_planta_anual = brecha_total_planta_semanal * 52.0
        
        # 1. Estrategia 100% Nuevas Contrataciones
        hc_adicional_100 = brecha_total_planta_semanal / meta_horas_semanales
        costo_anual_100_contrataciones = hc_adicional_100 * (
            (salario_diario * 365.0 * (1.0 + factor_prestaciones)) +
            (costo_comedor_transporte_mensual * 12.0)
        )
        
        # 2. Estrategia 100% Tiempo Extra (Teórico - riesgoso legalmente)
        # Primeras 9h dobles, excedente triple
        h_dobles = min(horas_efectivas_a_cubrir_persona, 9.0)
        h_triples = max(0.0, horas_efectivas_a_cubrir_persona - 9.0)
        costo_anual_tiempo_extra = (
            (h_dobles * salario_hora * 2.0 + h_triples * salario_hora * 3.0) *
            52.0 * headcount_op
        )
        riesgo_legal_tiempo_extra = h_triples > 0 or horas_efectivas_a_cubrir_persona > 9.0
        
        # 3. Estrategia Mixta Recomendada por Catch Consulting:
        # 40% Cobertura con contratación escalonada
        # 35% Optimización de balanceo de líneas y reingeniería de turnos
        # 25% Cobertura con horas extras dobles planificadas
        hc_mixto = hc_adicional_100 * 0.40
        costo_contratacion_mixto = hc_mixto * (
            (salario_diario * 365.0 * (1.0 + factor_prestaciones)) +
            (costo_comedor_transporte_mensual * 12.0)
        )
        horas_extra_mixto_persona = horas_efectivas_a_cubrir_persona * 0.25
        costo_extra_mixto = (horas_extra_mixto_persona * salario_hora * 2.0) * 52.0 * headcount_op
        costo_anual_mixto = costo_contratacion_mixto + costo_extra_mixto
        
        # 4. Estrategia Turno Comprimido 4x3 (4 días de 10 horas)
        # Cero horas extra regulares, reducción de días de comedor y transporte de 6 a 4 días (-33% costo logístico)
        ahorro_transporte_comedor = (headcount_op * costo_comedor_transporte_mensual * 12.0) * 0.25
        costo_anual_4x3 = max(0.0, (hc_adicional_100 * 0.20 * salario_diario * 365 * (1.0 + factor_prestaciones)) - ahorro_transporte_comedor)

        return {
            "company": company_name,
            "headcount_operativo": headcount_op,
            "salario_diario_promedio": round(salario_diario, 2),
            "salario_hora": round(salario_hora, 2),
            "horas_semanales_actuales": horas_actuales,
            "meta_horas_semanales": meta_horas_semanales,
            "brecha_horas_semanal_persona": round(brecha_horas_persona, 2),
            "horas_efectivas_a_cubrir_persona": round(horas_efectivas_a_cubrir_persona, 2),
            "brecha_total_planta_semanal": round(brecha_total_planta_semanal, 1),
            "brecha_total_planta_anual": round(brecha_total_planta_anual, 1),
            "estrategias": {
                "100_NUEVAS_CONTRATACIONES": {
                    "headcount_adicional": round(hc_adicional_100, 1),
                    "pct_aumento_plantilla": round((hc_adicional_100 / headcount_op) * 100, 2) if headcount_op > 0 else 0,
                    "costo_anual_mxn": round(costo_anual_100_contrataciones, 2),
                    "costo_mensual_mxn": round(costo_anual_100_contrataciones / 12.0, 2),
                    "viabilidad": "Alta operacionalmente, requiere esfuerzo de reclutamiento",
                    "riesgo_legal": "Nulo (100% cumplimiento LFT)"
                },
                "100_TIEMPO_EXTRA": {
                    "headcount_adicional": 0.0,
                    "pct_aumento_plantilla": 0.0,
                    "costo_anual_mxn": round(costo_anual_tiempo_extra, 2),
                    "costo_mensual_mxn": round(costo_anual_tiempo_extra / 12.0, 2),
                    "viabilidad": "No recomendada a largo plazo",
                    "riesgo_legal": "ALTO: Incurre en horas triples, riesgo de multas STPS y fatiga extrema" if riesgo_legal_tiempo_extra else "Medio"
                },
                "MIXTA_RECOMENDADA_CATCH": {
                    "headcount_adicional": round(hc_mixto, 1),
                    "pct_aumento_plantilla": round((hc_mixto / headcount_op) * 100, 2) if headcount_op > 0 else 0,
                    "costo_anual_mxn": round(costo_anual_mixto, 2),
                    "costo_mensual_mxn": round(costo_anual_mixto / 12.0, 2),
                    "ahorro_vs_100_contrataciones_pct": round((1.0 - (costo_anual_mixto / costo_anual_100_contrataciones)) * 100, 1) if costo_anual_100_contrataciones > 0 else 0,
                    "viabilidad": "Óptima: Balance entre costo, flexibilidad y cumplimiento",
                    "riesgo_legal": "Controlado (dentro de topes de 9h dobles)"
                },
                "COMPRIMIDA_4X3_10H": {
                    "headcount_adicional": round(hc_adicional_100 * 0.20, 1),
                    "costo_anual_mxn": round(costo_anual_4x3, 2),
                    "costo_mensual_mxn": round(costo_anual_4x3 / 12.0, 2),
                    "beneficio_colaborador": "3 días continuos de descanso a la semana, menor rotación y ausentismo",
                    "viabilidad": "Alta para plantas con procesos continuos"
                }
            }
        }

    def simular_cluster_total(self, meta_horas: float = 40.0) -> Dict[str, Any]:
        """Calcula el impacto global consolidado para todas las empresas de la base histórica."""
        total_hc_actual = 0.0
        total_brecha_horas_sem = 0.0
        total_hc_nuevo_req = 0.0
        total_costo_anual_contratacion = 0.0
        total_costo_anual_mixto = 0.0
        
        for comp in self.df['company'].unique():
            res = self.simular_empresa(comp, meta_horas_semanales=meta_horas)
            total_hc_actual += res['headcount_operativo']
            total_brecha_horas_sem += res['brecha_total_planta_semanal']
            total_hc_nuevo_req += res['estrategias']['100_NUEVAS_CONTRATACIONES']['headcount_adicional']
            total_costo_anual_contratacion += res['estrategias']['100_NUEVAS_CONTRATACIONES']['costo_anual_mxn']
            total_costo_anual_mixto += res['estrategias']['MIXTA_RECOMENDADA_CATCH']['costo_anual_mxn']
            
        return {
            "universo_empresas": int(self.df['company'].nunique()),
            "headcount_operativo_total": round(total_hc_actual, 0),
            "brecha_semanal_horas_cluster": round(total_brecha_horas_sem, 0),
            "brecha_anual_horas_cluster": round(total_brecha_horas_sem * 52.0, 0),
            "headcount_adicional_requerido": round(total_hc_nuevo_req, 0),
            "pct_crecimiento_empleo": round((total_hc_nuevo_req / total_hc_actual) * 100, 2) if total_hc_actual > 0 else 0,
            "costo_anual_total_contratacion_mxn": round(total_costo_anual_contratacion, 2),
            "costo_anual_total_mixto_mxn": round(total_costo_anual_mixto, 2),
            "ahorro_total_estrategia_mixta_mxn": round(total_costo_anual_contratacion - total_costo_anual_mixto, 2)
        }
