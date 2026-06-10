"""
Modelo de propiedad inmobiliaria.

Define atributos, dinámicas y cálculos relacionados con la propiedad.
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Propiedad:
    """Representa una propiedad inmobiliaria."""

    valor_compra_uf: float
    """Valor de compra en UF."""

    fecha_compra: datetime
    """Fecha de adquisición."""

    ubicacion: str = "Gran Santiago"
    """Ubicación geográfica."""

    tipo: str = "Casa/Departamento"
    """Tipo de propiedad."""

    superficie_m2: Optional[float] = None
    """Superficie en metros cuadrados."""

    # Dinámicas
    tasas_apreciacion_anual: dict[str, float] = field(default_factory=dict)
    """Tasas de apreciación por escenario: {'BASE': 0.03, 'OPTIMISTA': 0.05, ...}"""

    def __post_init__(self):
        if not self.tasas_apreciacion_anual:
            self.tasas_apreciacion_anual = {
                'PESIMISTA': 0.01,
                'BASE': 0.03,
                'OPTIMISTA': 0.05,
            }

    def valor_futuro_uf(
        self,
        meses_transcurridos: int,
        escenario: str = "BASE",
    ) -> float:
        """
        Calcula el valor futuro de la propiedad.

        Args:
            meses_transcurridos: Número de meses desde la compra.
            escenario: Escenario macroeconómico.

        Returns:
            Valor de la propiedad en UF.
        """
        tasa_anual = self.tasas_apreciacion_anual.get(escenario, 0.03)
        tasa_mensual = (1 + tasa_anual) ** (1 / 12) - 1
        return self.valor_compra_uf * ((1 + tasa_mensual) ** meses_transcurridos)

    def plusvalia_uf(
        self,
        meses_transcurridos: int,
        escenario: str = "BASE",
    ) -> float:
        """
        Calcula la plusvalía (ganancia) de la propiedad.

        Returns:
            Plusvalía en UF.
        """
        return self.valor_futuro_uf(meses_transcurridos, escenario) - self.valor_compra_uf
