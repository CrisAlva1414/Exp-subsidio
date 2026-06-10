"""
Modelo de ingresos.

Define proyecciones de ingresos brutos, líquidos y escenarios.
"""

from dataclasses import dataclass


@dataclass
class Ingreso:
    """Representa proyecciones de ingreso mensual."""

    ingreso_bruto_mes_0_uf: float
    """Ingreso bruto mensual inicial en UF."""

    tasa_crecimiento_anual: dict[str, float]
    """Tasas de crecimiento anual por escenario."""

    tasa_impuesto_marginal_nominal: float = 0.20
    """Tasa de impuesto marginal (simplificado)."""

    def ingreso_bruto_uf(
        self,
        meses_transcurridos: int,
        escenario: str = "BASE",
    ) -> float:
        """
        Calcula el ingreso bruto en un mes específico.

        Args:
            meses_transcurridos: Número de meses desde mes 0.
            escenario: Escenario de ingresos.

        Returns:
            Ingreso bruto mensual en UF.
        """
        tasa_anual = self.tasa_crecimiento_anual.get(escenario, 0.02)
        tasa_mensual = (1 + tasa_anual) ** (1 / 12) - 1
        return self.ingreso_bruto_mes_0_uf * ((1 + tasa_mensual) ** meses_transcurridos)

    def ingreso_liquido_uf(
        self,
        meses_transcurridos: int,
        escenario: str = "BASE",
    ) -> float:
        """
        Calcula el ingreso líquido (después de impuestos).

        Args:
            meses_transcurridos: Número de meses desde mes 0.
            escenario: Escenario de ingresos.

        Returns:
            Ingreso líquido mensual en UF.
        """
        bruto = self.ingreso_bruto_uf(meses_transcurridos, escenario)
        return bruto * (1 - self.tasa_impuesto_marginal_nominal)
