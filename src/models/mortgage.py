"""
Modelo de hipoteca.

Define estructura de deuda hipotecaria y parámetros de amortización.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Hipoteca:
    """Representa un crédito hipotecario."""

    monto_inicial_uf: float
    """Monto inicial del crédito en UF."""

    plazo_meses: int
    """Plazo de amortización en meses."""

    tasa_anual_nominal: dict[str, float]
    """Tasa anual nominal por escenario."""

    fecha_inicio: datetime
    """Fecha de otorgamiento del crédito."""

    def tasa_mensual(self, escenario: str = "BASE") -> float:
        """
        Retorna la tasa mensual del crédito.

        Args:
            escenario: Escenario macroeconómico.

        Returns:
            Tasa mensual (decimal).
        """
        tasa_anual = self.tasa_anual_nominal.get(escenario, 0.04)
        return (1 + tasa_anual) ** (1 / 12) - 1

    def dividendo_uf(
        self,
        escenario: str = "BASE",
    ) -> float:
        """
        Calcula el dividendo (cuota) mensual fijo.

        Utiliza fórmula de amortización francesa (cuota fija).

        Args:
            escenario: Escenario macroeconómico.

        Returns:
            Dividendo mensual en UF.
        """
        r = self.tasa_mensual(escenario)
        n = self.plazo_meses

        if r == 0:
            return self.monto_inicial_uf / n

        numerador = r * ((1 + r) ** n)
        denominador = ((1 + r) ** n) - 1

        return self.monto_inicial_uf * (numerador / denominador)
