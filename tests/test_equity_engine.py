"""
Tests para EquityEngine.
"""

import pytest
from datetime import datetime
from src.models.property import Propiedad
from src.engines.equity_engine import EquityEngine


def test_equity_monthly_construction():
    """Valida construcción de tabla de patrimonio."""
    propiedad = Propiedad(
        valor_compra_uf=300.0,
        fecha_compra=datetime(2025, 1, 1),
        tasas_apreciacion_anual={'BASE': 0.03},
    )

    # Saldos simulados (decrece a 0)
    saldo_deuda = [300.0 - (i * 1.25) for i in range(361)]
    saldo_deuda = [max(0, s) for s in saldo_deuda]

    # Ahorros (crece)
    ahorros = [i * 0.5 for i in range(361)]

    engine = EquityEngine()
    df = engine.build_equity_monthly(propiedad, saldo_deuda, ahorros, 'BASE')

    assert len(df) == 361
    assert 'patrimonio_neto' in df.columns
    assert df['patrimonio_neto'].iloc[-1] > df['patrimonio_neto'].iloc[0]
