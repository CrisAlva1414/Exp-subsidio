"""
Modelo de hogar.

Define gastos y dinámicas del hogar.
"""

from dataclasses import dataclass, field


@dataclass
class Hogar:
    """Representa los gastos del hogar."""

    gastos_mensuales_base_uf: dict[str, float] = field(default_factory=dict)
    """Gastos mensuales base por categoría en UF.

    Categorías: servicios_basicos, mantenimiento, seguros, administracion, otros.
    """

    tasa_crecimiento_gasto_anual: float = 0.02
    """Tasa de crecimiento anual de gastos."""

    def __post_init__(self):
        if not self.gastos_mensuales_base_uf:
            self.gastos_mensuales_base_uf = {
                'servicios_basicos': 0.5,
                'mantenimiento': 0.3,
                'seguros': 0.2,
                'administracion': 0.0,
                'otros': 0.0,
            }

    def gastos_mensuales_uf(
        self,
        meses_transcurridos: int,
    ) -> float:
        """
        Calcula los gastos mensuales totales.

        Args:
            meses_transcurridos: Número de meses desde mes 0.

        Returns:
            Gastos mensuales totales en UF.
        """
        tasa_mensual = (1 + self.tasa_crecimiento_gasto_anual) ** (1 / 12) - 1
        gastos_base = sum(self.gastos_mensuales_base_uf.values())
        return gastos_base * ((1 + tasa_mensual) ** meses_transcurridos)

    def desglose_gastos_uf(
        self,
        meses_transcurridos: int,
    ) -> dict[str, float]:
        """
        Retorna el desglose de gastos por categoría.

        Args:
            meses_transcurridos: Número de meses desde mes 0.

        Returns:
            Diccionario con gastos por categoría.
        """
        tasa_mensual = (1 + self.tasa_crecimiento_gasto_anual) ** (1 / 12) - 1
        factor = (1 + tasa_mensual) ** meses_transcurridos

        return {
            categoria: monto * factor
            for categoria, monto in self.gastos_mensuales_base_uf.items()
        }
