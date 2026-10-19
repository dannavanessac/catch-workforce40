"""
Módulo de Reglas Normativas de la Ley Federal del Trabajo (LFT) de México
Especializado en jornada laboral, turnos, descansos y horas extraordinarias.
"""
from typing import Dict, List, Tuple, Any
import numpy as np

# Valor de la UMA (Unidad de Medida y Actualización) para cálculos de multas y exenciones
VALOR_UMA_DIARIO = 113.14  # Referencia vigente en México

class LFTRulesEngine:
    """Motor de validación legal y cálculo de jornadas y horas extraordinarias conforme a la LFT."""
    
    LIMITES_JORNADA = {
        "DIURNA": {
            "rango_horas": "06:00 a 20:00",
            "max_diario": 8.0,
            "max_semanal_actual": 48.0,
            "max_semanal_reforma": 40.0,
            "art_lft": "Art. 60 y 61 LFT"
        },
        "NOCTURNA": {
            "rango_horas": "20:00 a 06:00",
            "max_diario": 7.0,
            "max_semanal_actual": 42.0,
            "max_semanal_reforma": 35.0,
            "art_lft": "Art. 60 y 61 LFT"
        },
        "MIXTA": {
            "rango_horas": "Comprende periodos diurnos y nocturnos (menos de 3.5 hrs nocturnas)",
            "max_diario": 7.5,
            "max_semanal_actual": 45.0,
            "max_semanal_reforma": 37.5,
            "art_lft": "Art. 60 y 61 LFT"
        }
    }

    @staticmethod
    def calcular_horas_extra(
        horas_extra_por_dia: List[float],
        salario_diario: float,
        tipo_jornada: str = "DIURNA"
    ) -> Dict[str, Any]:
        """
        Calcula el desglose legal de horas dobles y triples según los artículos 66, 67 y 68 de la LFT:
        - Máximo 3 horas diarias en máximo 3 días a la semana = hasta 9 horas al doble (recargo 100%).
        - Cualquier hora diaria que exceda de 3, o las horas en un 4to día o posteriores, o el exceso de 9 semanales = triples (recargo 200%).
        """
        duracion_jornada = LFTRulesEngine.LIMITES_JORNADA.get(tipo_jornada.upper(), LFTRulesEngine.LIMITES_JORNADA["DIURNA"])["max_diario"]
        salario_por_hora = salario_diario / duracion_jornada
        
        costo_hora_doble = salario_por_hora * 2.0
        costo_hora_triple = salario_por_hora * 3.0
        
        horas_dobles = 0.0
        horas_triples = 0.0
        dias_con_tiempo_extra = 0
        infracciones = []
        
        # Evaluar día a día
        for dia_idx, h in enumerate(horas_extra_por_dia):
            if h <= 0:
                continue
            dias_con_tiempo_extra += 1
            
            # Si ya se agotaron los 3 días de tiempo extra permitidos por semana
            if dias_con_tiempo_extra > 3:
                horas_triples += h
                infracciones.append(f"Día {dia_idx + 1}: Exceso de días con tiempo extra ({dias_con_tiempo_extra}° día, máx 3 días permitidos por Art. 66 LFT). Todas las {h:.1f} hrs se pagan al triple.")
            else:
                # Si en el día labora hasta 3 horas extras
                if h <= 3.0:
                    # Verificar si al sumar al acumulado de dobles supera 9
                    if (horas_dobles + h) <= 9.0:
                        horas_dobles += h
                    else:
                        disponibles = 9.0 - horas_dobles
                        horas_dobles += disponibles
                        exceso = h - disponibles
                        horas_triples += exceso
                        infracciones.append(f"Día {dia_idx + 1}: Se alcanzó el tope semanal de 9 hrs dobles. {exceso:.1f} hrs pasan a triples.")
                else:
                    # El día tuvo más de 3 horas
                    infracciones.append(f"Día {dia_idx + 1}: Se superó el límite diario de 3 hrs extras ({h:.1f} hrs reportadas). El excedente de {h - 3.0:.1f} hrs se paga al triple.")
                    dobles_posibles = min(3.0, max(0.0, 9.0 - horas_dobles))
                    horas_dobles += dobles_posibles
                    horas_triples += (h - dobles_posibles)
                    
        total_horas_extra = horas_dobles + horas_triples
        monto_dobles = horas_dobles * costo_hora_doble
        monto_triples = horas_triples * costo_hora_triple
        monto_total_extra = monto_dobles + monto_triples
        
        # Riesgo de sanción STPS (Art. 994 Fracción I LFT: 50 a 5000 UMAs por violaciones a la jornada)
        tiene_infraccion = len(infracciones) > 0 or total_horas_extra > 9.0
        multa_min_mxn = 50 * VALOR_UMA_DIARIO if tiene_infraccion else 0.0
        multa_max_mxn = 2500 * VALOR_UMA_DIARIO if tiene_infraccion else 0.0
        
        return {
            "salario_diario": salario_diario,
            "salario_hora": salario_por_hora,
            "total_horas_extra": round(total_horas_extra, 2),
            "horas_dobles": round(horas_dobles, 2),
            "horas_triples": round(horas_triples, 2),
            "monto_dobles_mxn": round(monto_dobles, 2),
            "monto_triples_mxn": round(monto_triples, 2),
            "monto_total_extra_mxn": round(monto_total_extra, 2),
            "dias_con_extra": dias_con_tiempo_extra,
            "tiene_infracciones": tiene_infraccion,
            "infracciones_detectadas": infracciones,
            "multa_estimada_stps": {
                "min_mxn": multa_min_mxn,
                "max_mxn": multa_max_mxn
            }
        }

    @staticmethod
    def validar_turno(horario_entrada_str: str, horario_salida_str: str, dias_semana: int) -> Dict[str, Any]:
        """Evalúa un turno contra los límites de jornada diurna, mixta o nocturna."""
        # Heurística de tipo de turno
        h_ent = str(horario_entrada_str).lower()
        if "06:" in h_ent or "07:" in h_ent or "08:" in h_ent or "09:" in h_ent:
            tipo = "DIURNA"
        elif "14:" in h_ent or "15:" in h_ent or "16:" in h_ent:
            tipo = "MIXTA"
        elif "22:" in h_ent or "23:" in h_ent or "00:" in h_ent:
            tipo = "NOCTURNA"
        else:
            tipo = "DIURNA"
            
        norma = LFTRulesEngine.LIMITES_JORNADA[tipo]
        horas_semana_actual = dias_semana * norma["max_diario"]
        brecha_40h = max(0.0, horas_semana_actual - norma["max_semanal_reforma"])
        
        return {
            "tipo_jornada": tipo,
            "norma": norma,
            "dias_semana": dias_semana,
            "horas_semanales_actuales": horas_semana_actual,
            "horas_semanales_reforma": norma["max_semanal_reforma"],
            "brecha_semanal_por_trabajador": brecha_40h,
            "cumple_40h_actualmente": (brecha_40h == 0.0)
        }
