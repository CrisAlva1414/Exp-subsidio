"""
MortgageEngine: cálculos de hipoteca y tabla de amortización.

Responsable de:
- Construir tabla de amortización completa
- Calcular dividendo, interés, amortización, saldo por mes
- Validar elegibilidad y restricciones
"""

import pandas as pd
from src.models.mortgage import Hipoteca


class MortgageEngine:
    """Motor de cálculo de hipotecas."""

    def __init__(self):
        pass

    def build_amortization_table(
        self,
        hipoteca: Hipoteca,
        escenario: str = "BASE",
    ) -> pd.DataFrame:
        """
        Construye tabla de amortización mensual completa.

        Returns:
            DataFrame con columnas:
            - mes
            - dividendo
            - interes
            - amortizacion
            - saldo_insoluto
        """
        meses = []
        dividendos = []
        intereses = []
        amortizaciones = []
        saldos = []

        tasa_mensual = hipoteca.tasa_mensual(escenario)
        dividendo = hipoteca.dividendo_uf(escenario)
        saldo = hipoteca.monto_inicial_uf

        for mes in range(1, hipoteca.plazo_meses + 1):
            interes = saldo * tasa_mensual
            amortizacion = dividendo - interes
            saldo -= amortizacion

            # Evitar negativos por redondeo
            if saldo < 0:
                saldo = 0

            meses.append(mes)
            dividendos.append(dividendo)
            intereses.append(interes)
            amortizaciones.append(amortizacion)
            saldos.append(saldo)

        return pd.DataFrame({
            'mes': meses,
            'dividendo': dividendos,
            'interes': intereses,
            'amortizacion': amortizaciones,
            'saldo_insoluto': saldos,
        })

    def dividendo_en_mes(
        self,
        hipoteca: Hipoteca,
        mes: int,
        escenario: str = "BASE",
    ) -> float:
        """Retorna el dividendo en un mes específico."""
        if mes > hipoteca.plazo_meses:
            return 0.0
        return hipoteca.dividendo_uf(escenario)
