"""
Tests para CashflowEngine.
"""

import pytest
from src.models.income import Ingreso
from src.models.household import Hogar
from src.engines.cashflow_engine import CashflowEngine


def test_cashflow_monthly_construction():
    """Valida construcción de tabla de cashflow."""
    ingreso = Ingreso(
        ingreso_bruto_mes_0_uf=50.0,
        tasa_crecimiento_anual={'BASE': 0.02},
    )

    hogar = Hogar(
        gastos_mensuales_base_uf={
            'servicios_basicos': 0.5,
            'mantenimiento': 0.3,
            'seguros': 0.2,
            'administracion': 0.0,
            'otros': 0.0,
        }
    )

    dividendos = [3.0] * 240 + [0.0] * 121  # 20 años de hipoteca + 10 años sin

    engine = CashflowEngine()
    df = engine.build_cashflow_monthly(
        ingreso,
        hogar,
        dividendos,
        'BASE',
        'BASE',
    )

    assert len(df) == 361
    assert 'flujo_libre' in df.columns
    assert 'ahorro_acumulado' in df.columns
    assert df['ahorro_acumulado'].iloc[-1] > 0  # Debe acumular positivo
