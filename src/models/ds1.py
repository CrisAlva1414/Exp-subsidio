"""
Modelo del subsidio DS1.

Define características de los tramos 2 y 3 del subsidio.
"""

from dataclasses import dataclass
from enum import Enum


class TramoSubsidio(str, Enum):
    """Tramos disponibles del subsidio DS1."""
    TRAMO_2 = "TRAMO_2"
    TRAMO_3 = "TRAMO_3"


@dataclass
class SubsidioDS1:
    """Representa un subsidio DS1 específico."""

    tramo: TramoSubsidio
    """Tramo del subsidio."""

    monto_subsidio_uf: float
    """Monto del subsidio en UF."""

    rango_precio_minimo_uf: float
    """Precio mínimo de la propiedad en UF."""

    rango_precio_maximo_uf: float
    """Precio máximo de la propiedad en UF."""

    rango_ingreso_minimo_uf: float
    """Ingreso mínimo para acceso en UF."""

    rango_ingreso_maximo_uf: float
    """Ingreso máximo para acceso en UF."""

    max_endeudamiento_pct: float = 70.0
    """Endeudamiento máximo como % del valor propiedad."""

    plazo_hipoteca_meses: int = 240
    """Plazo hipotecario permitido en meses (20 años)."""

    def es_elegible(
        self,
        valor_propiedad_uf: float,
        ingreso_liquido_mensual_uf: float,
    ) -> bool:
        """
        Verifica si la propiedad e ingreso cumplen requisitos del tramo.

        Args:
            valor_propiedad_uf: Valor de la propiedad en UF.
            ingreso_liquido_mensual_uf: Ingreso líquido mensual en UF.

        Returns:
            True si cumple requisitos, False en caso contrario.
        """
        precio_ok = (
            self.rango_precio_minimo_uf <= valor_propiedad_uf
            <= self.rango_precio_maximo_uf
        )

        ingreso_anual_uf = ingreso_liquido_mensual_uf * 12
        ingreso_ok = (
            self.rango_ingreso_minimo_uf <= ingreso_anual_uf
            <= self.rango_ingreso_maximo_uf
        )

        return precio_ok and ingreso_ok

    def monto_a_financiar_uf(
        self,
        valor_propiedad_uf: float,
    ) -> float:
        """
        Calcula el monto que se debe financiar.

        Monto a financiar = Valor - Subsidio - Ahorro requerido.

        Args:
            valor_propiedad_uf: Valor de la propiedad en UF.

        Returns:
            Monto a financiar en UF.
        """
        # Simplificación: el subsidio cubre parte del valor
        # El resto se financia con hipoteca (hasta max_endeudamiento_pct)
        max_financiamiento = valor_propiedad_uf * (self.max_endeudamiento_pct / 100.0)
        return max_financiamiento
