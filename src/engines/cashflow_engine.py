"""
CashflowEngine: cálculo de flujos de caja mensuales.

Responsable de:
- Calcular ingreso bruto y líquido por mes
- Restar dividendo, gastos, contribuciones
- Calcular flujo libre y ahorros acumulados
"""

import pandas as pd
from src.models.income import Ingreso
from src.models.household import Hogar
from src.config.config import MAX_DIVIDENDO_PCT_INGRESO


class CashflowEngine:
    """Motor de cálculo de flujos de caja."""

    def __init__(self):
        pass

    def build_cashflow_monthly(
        self,
        ingreso: Ingreso,
        hogar: Hogar,
        dividendos_mensuales: list[float],
        escenario_ingreso: str = "BASE",
        escenario_macro: str = "BASE",
    ) -> pd.DataFrame:
        """
        Construye tabla de flujos de caja mensuales.

        Returns:
            DataFrame con columnas:
            - mes
            - edad
            - ingreso_bruto
            - ingreso_liquido
            - dividendo
            - gastos
            - flujo_libre
            - ahorro_acumulado
            - ratio_dividendo_ingreso
        """
        meses = []
        edades = []
        ingresos_brutos = []
        ingresos_liquidos = []
        dividendos = []
        gastos = []
        flujos_libres = []
        ahorros_acumulados = []
        ratios_dividendo = []

        ahorro_acumulado = 0.0

        for mes in range(361):  # 0 a 360
            edad = 25 + (mes / 12)
            ingreso_bruto = ingreso.ingreso_bruto_uf(mes, escenario_ingreso)
            ingreso_liquido = ingreso.ingreso_liquido_uf(mes, escenario_ingreso)
            dividendo = dividendos_mensuales[mes] if mes < len(dividendos_mensuales) else 0.0
            gasto = hogar.gastos_mensuales_uf(mes)

            flujo_libre = ingreso_liquido - dividendo - gasto

            # Validar restricción de dividendo
            ratio_dividendo = (
                (dividendo / ingreso_liquido) if ingreso_liquido > 0 else 0.0
            )

            if ratio_dividendo > MAX_DIVIDENDO_PCT_INGRESO / 100.0:
                # Flag: violaría restricción
                pass

            ahorro_acumulado += flujo_libre

            meses.append(mes)
            edades.append(edad)
            ingresos_brutos.append(ingreso_bruto)
            ingresos_liquidos.append(ingreso_liquido)
            dividendos.append(dividendo)
            gastos.append(gasto)
            flujos_libres.append(flujo_libre)
            ahorros_acumulados.append(ahorro_acumulado)
            ratios_dividendo.append(ratio_dividendo)

        return pd.DataFrame({
            'mes': meses,
            'edad': edades,
            'ingreso_bruto': ingresos_brutos,
            'ingreso_liquido': ingresos_liquidos,
            'dividendo': dividendos,
            'gastos': gastos,
            'flujo_libre': flujos_libres,
            'ahorro_acumulado': ahorros_acumulados,
            'ratio_dividendo_ingreso': ratios_dividendo,
        })
