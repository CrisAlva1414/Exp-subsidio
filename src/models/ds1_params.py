"""
Parámetros reales del subsidio DS1 2024 (Chile).
Fuente: MINVU - Decreto Supremo N°1 (DS1)
"""

from dataclasses import dataclass
from src.models.ds1 import SubsidioDS1, TramoSubsidio


def get_subsidio_tramo2() -> SubsidioDS1:
    """
    DS1 Tramo 2: clase media emergente.
    - Valor propiedad: 1000 a 2000 UF
    - Ingreso familiar: hasta 25 UF/mes (300 UF/año)
    - Subsidio: 200 UF
    - Ahorro mínimo requerido: 30 UF
    - Financiamiento hipotecario: hasta 80% del valor
    """
    return SubsidioDS1(
        tramo=TramoSubsidio.TRAMO_2,
        monto_subsidio_uf=200.0,
        rango_precio_minimo_uf=1000.0,
        rango_precio_maximo_uf=2000.0,
        rango_ingreso_minimo_uf=0.0,       # Sin mínimo formal
        rango_ingreso_maximo_uf=300.0,     # 25 UF/mes × 12
        max_endeudamiento_pct=80.0,
        plazo_hipoteca_meses=240,
    )


def get_subsidio_tramo3() -> SubsidioDS1:
    """
    DS1 Tramo 3: clase media consolidada.
    - Valor propiedad: 2000 a 3000 UF
    - Ingreso familiar: hasta 40 UF/mes (480 UF/año)
    - Subsidio: 100 UF
    - Ahorro mínimo requerido: 50 UF
    - Financiamiento hipotecario: hasta 80% del valor
    """
    return SubsidioDS1(
        tramo=TramoSubsidio.TRAMO_3,
        monto_subsidio_uf=100.0,
        rango_precio_minimo_uf=2000.0,
        rango_precio_maximo_uf=3000.0,
        rango_ingreso_minimo_uf=0.0,
        rango_ingreso_maximo_uf=480.0,     # 40 UF/mes × 12
        max_endeudamiento_pct=80.0,
        plazo_hipoteca_meses=240,
    )


@dataclass
class PerfilICI:
    """Perfil de Ingeniero Civil Industrial, Santiago, 25 años, 2024."""
    
    # Ingreso inicial (UF/mes) - ICI recién egresado, Santiago
    ingreso_bruto_inicial_uf: float = 22.0     # ~$1.7M CLP/mes
    
    # Ahorro acumulado al comprar (UF) - 3 años trabajando
    ahorro_inicial_uf: float = 80.0
    
    # Tasas crecimiento ingreso anual por escenario
    tasas_crecimiento: dict = None
    
    # Tasa impuesto efectiva (simplificada)
    tasa_impuesto: float = 0.12              # 12% efectivo con descuentos
    
    def __post_init__(self):
        if self.tasas_crecimiento is None:
            self.tasas_crecimiento = {
                'PESIMISTA': 0.01,           # 1% real anual
                'BASE':      0.02,           # 2% real anual
                'OPTIMISTA': 0.04,           # 4% real anual (con ascensos)
            }