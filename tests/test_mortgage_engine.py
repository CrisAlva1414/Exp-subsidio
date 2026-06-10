"""
Tests para MortgageEngine.
"""

import pytest
from datetime import datetime
from src.models.mortgage import Hipoteca
from src.engines.mortgage_engine import MortgageEngine


def test_dividendo_calculation():
    """Valida cálculo de dividendo."""
    hipoteca = Hipoteca(
        monto_inicial_uf=500.0,
        plazo_meses=240,
        tasa_anual_nominal={'BASE': 0.04},
        fecha_inicio=datetime(2025, 1, 1),
    )

    engine = MortgageEngine()
    dividendo = hipoteca.dividendo_uf('BASE')

    # Validar que sea positivo y razonable
    assert dividendo > 0
    assert dividendo < hipoteca.monto_inicial_uf  # Validez teórica

    # Dividendo 20 años a 4% anual debe estar alrededor de 3.05 UF
    # (estimación: capital/plazo ~ 2.08, interés ~ 1.67)
    assert 2.5 < dividendo < 3.5


def test_amortization_table():
    """Valida tabla de amortización."""
    hipoteca = Hipoteca(
        monto_inicial_uf=500.0,
        plazo_meses=240,
        tasa_anual_nominal={'BASE': 0.04},
        fecha_inicio=datetime(2025, 1, 1),
    )

    engine = MortgageEngine()
    df = engine.build_amortization_table(hipoteca, 'BASE')

    # Validaciones
    assert len(df) == 240
    assert df['saldo_insoluto'].iloc[-1] < 0.01  # Debe ser ~0
    assert (df['dividendo'] == df.iloc[0]['dividendo']).all()  # Cuota fija
    assert (df['interes'] > 0).all()
    assert (df['amortizacion'] > 0).all()
