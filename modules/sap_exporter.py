"""
Módulo de Integración SAP HCM / SuccessFactors
Genera layouts estándar de tiempos y nómina para Infotipos 2001, 2002 y 2005.
"""
from typing import List, Dict, Any
import pandas as pd
import datetime

class SAPHCMExporter:
    """Generador de archivos de interfaz para SAP HCM (Tiempos y Nómina)."""
    
    @staticmethod
    def generar_infotipo_2001(ausencias: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Infotipo 2001: Ausentismos / Incapacidades / Vacaciones.
        Campos estándar de SAP:
        - PERNR: Número de personal (8 dígitos)
        - INFTY: '2001'
        - SUBTY: Subtipo de ausencia (0100: Enfermedad, 0200: Accidente, 0300: Falta, 0400: Vacaciones)
        - BEGDA: Fecha de inicio (AAAAMMDD)
        - ENDDA: Fecha de fin (AAAAMMDD)
        - STDAZ: Horas de ausencia
        - SPRPS: Bloqueo de nómina (espacio o 'X')
        """
        records = []
        for a in ausencias:
            records.append({
                "PERNR": str(a.get("pernr", "00000001")).zfill(8),
                "INFTY": "2001",
                "SUBTY": str(a.get("subty", "0300")),
                "BEGDA": a.get("begda", datetime.date.today().strftime("%Y%m%d")),
                "ENDDA": a.get("endda", datetime.date.today().strftime("%Y%m%d")),
                "STDAZ": f"{float(a.get('stdaz', 8.0)):.2f}",
                "MOTIVO": a.get("motivo", "Ausentismo Justificado"),
                "SPRPS": ""
            })
        return pd.DataFrame(records)

    @staticmethod
    def generar_infotipo_2002(presencias: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Infotipo 2002: Presencias y Turnos Planificados.
        - PERNR: Número de personal
        - INFTY: '2002'
        - SUBTY: Subtipo de presencia (0800: Jornada Ordinaria, 0810: Turno 12h, 0820: Turno Mixto)
        - BEGDA: Fecha inicio
        - ENDDA: Fecha fin
        - STDAZ: Horas programadas
        - TPROG: Clave del programa de turno (ej. 'D08', 'N07', 'M75', 'T12')
        """
        records = []
        for p in presencias:
            records.append({
                "PERNR": str(p.get("pernr", "00000001")).zfill(8),
                "INFTY": "2002",
                "SUBTY": str(p.get("subty", "0800")),
                "BEGDA": p.get("begda", datetime.date.today().strftime("%Y%m%d")),
                "ENDDA": p.get("endda", datetime.date.today().strftime("%Y%m%d")),
                "STDAZ": f"{float(p.get('stdaz', 8.0)):.2f}",
                "TPROG": p.get("tprog", "D08"),
                "TURNO_DESCRIP": p.get("descripcion", "Turno Diurno Ordinario 8h")
            })
        return pd.DataFrame(records)

    @staticmethod
    def generar_infotipo_2005(horas_extras: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Infotipo 2005: Horas Extraordinarias (Overtime).
        - PERNR: Número de personal
        - INFTY: '2005'
        - SUBTY: 1010 (Horas Extras Dobles 100%), 1020 (Horas Extras Triples 200%)
        - BEGDA: Fecha de devengo
        - ENDDA: Fecha de devengo
        - LGART: CC-Nómina (Wage Type: HEDO, HETR)
        - ANZHL: Cantidad de horas
        - BETRG: Importe liquidado en MXN
        - WAERS: 'MXN'
        """
        records = []
        for h in horas_extras:
            records.append({
                "PERNR": str(h.get("pernr", "00000001")).zfill(8),
                "INFTY": "2005",
                "SUBTY": str(h.get("subty", "1010")),
                "BEGDA": h.get("begda", datetime.date.today().strftime("%Y%m%d")),
                "ENDDA": h.get("endda", datetime.date.today().strftime("%Y%m%d")),
                "LGART": "HEDO" if str(h.get("subty")) == "1010" else "HETR",
                "ANZHL": f"{float(h.get('anzhl', 1.0)):.2f}",
                "BETRG": f"{float(h.get('betrg', 0.0)):.2f}",
                "WAERS": "MXN"
            })
        return pd.DataFrame(records)

    @staticmethod
    def exportar_layout_plano_sap(df: pd.DataFrame, infotipo: str) -> str:
        """Genera un string de texto con el formato plano de ancho fijo para SAP Batch Input."""
        lines = []
        header = f"# INTERFAZ SAP HCM - CARGA MASIVA INFOTIPO {infotipo} - GENERADO POR CATCH WORKFORCE"
        lines.append(header)
        for _, row in df.iterrows():
            line = " ".join([f"{k}:{v}" for k, v in row.items()])
            lines.append(line)
        return "\n".join(lines)
