"""
Modelo macroeconómico.

Define tasas de interés, inflación y otras variables macro por escenario.
"""

from dataclasses import dataclass, field


@dataclass
class EscenarioMacro:
    """Representa un escenario macroeconómico."""

    nombre: str
    """Nombre del escenario: PESIMISTA, BASE, OPTIMISTA."""

    # Tasas de interés
    tasa_hipotecaria_anual: float
    """Tasa hipotecaria anual nominal."""

    tasa_plazo_anual: float
    """Tasa de plazo anual para ahorros/inversiones."""

    # Inflación
    tasa_inflacion_anual: float
    """Tasa de inflación anual."""

    # Apreciación de propiedades
    tasa_apreciacion_propiedad_anual: float
    """Tasa anual de apreciación de propiedades."""

    # Crecimiento de ingresos
    tasa_crecimiento_ingreso_anual: float
    """Tasa anual de crecimiento de ingresos."""

    # Dinámicas
    cambios_estructurales: dict[str, float] = field(default_factory=dict)
    """Cambios estructurales por período (desempleo, etc.)."""

    def __repr__(self) -> str:
        return (
            f"EscenarioMacro(nombre={self.nombre}, "
            f"TPM={self.tasa_hipotecaria_anual:.1%}, "
            f"Inflación={self.tasa_inflacion_anual:.1%})"
        )
