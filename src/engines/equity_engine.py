"""
EquityEngine: cálculo del patrimonio neto.

Responsable de:
- Actualizar valor de propiedad (apreciación)
- Restar saldo deuda
- Calcular plusvalía
- Proyectar patrimonio neto mes a mes
"""

import pandas as pd
from src.models.property import Propiedad


class EquityEngine:
    """Motor de cálculo de patrimonio neto."""

    def __init__(self):
        pass

    def build_equity_monthly(
        self,
        propiedad: Propiedad,
        saldo_hipotecario_mensual: list[float],
        ahorro_acumulado_mensual: list[float],
        escenario: str = "BASE",
    ) -> pd.DataFrame:
        """
        Construye tabla de patrimonio neto mensual.

        Args:
            propiedad: Objeto Propiedad.
            saldo_hipotecario_mensual: Lista de saldos mensuales.
            ahorro_acumulado_mensual: Lista de ahorros acumulados.
            escenario: Escenario macroeconómico.

        Returns:
            DataFrame con columnas:
            - mes
            - valor_propiedad
            - plusvalia
            - saldo_deuda
            - ahorros
            - patrimonio_neto
        """
        meses = []
        valores_propiedad = []
        plusvalias = []
        saldos_deuda = []
        ahorros = []
        patrimonios_netos = []

        for mes in range(len(saldo_hipotecario_mensual)):
            valor_prop = propiedad.valor_futuro_uf(mes, escenario)
            plusvalia = propiedad.plusvalia_uf(mes, escenario)
            saldo_deuda = saldo_hipotecario_mensual[mes]
            ahorro = ahorro_acumulado_mensual[mes]

            patrimonio_neto = valor_prop + ahorro - saldo_deuda

            meses.append(mes)
            valores_propiedad.append(valor_prop)
            plusvalias.append(plusvalia)
            saldos_deuda.append(saldo_deuda)
            ahorros.append(ahorro)
            patrimonios_netos.append(patrimonio_neto)

        return pd.DataFrame({
            'mes': meses,
            'valor_propiedad': valores_propiedad,
            'plusvalia': plusvalias,
            'saldo_deuda': saldos_deuda,
            'ahorros': ahorros,
            'patrimonio_neto': patrimonios_netos,
        })
