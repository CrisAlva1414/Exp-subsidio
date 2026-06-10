"""
ScenarioEngine: construcción y gestión de escenarios.

Responsable de:
- Cargar escenarios desde datos
- Combinar escenarios de ingresos y macro
- Exponer escenarios a otros engines
"""

from src.models.macro import EscenarioMacro


class ScenarioEngine:
    """Gestor de escenarios macroeconómicos e ingresos."""

    def __init__(self, data_manager):
        self.data_manager = data_manager
        self._escenarios_macro = {}
        self._escenarios_ingresos = {}
        self._inicializar()

    def _inicializar(self):
        """Construye escenarios desde datos."""
        # Placeholder: será llenado en FASE 3 con datos reales
        self._escenarios_macro = {
            'PESIMISTA': EscenarioMacro(
                nombre='PESIMISTA',
                tasa_hipotecaria_anual=0.06,
                tasa_plazo_anual=0.02,
                tasa_inflacion_anual=0.04,
                tasa_apreciacion_propiedad_anual=0.01,
                tasa_crecimiento_ingreso_anual=0.01,
            ),
            'BASE': EscenarioMacro(
                nombre='BASE',
                tasa_hipotecaria_anual=0.04,
                tasa_plazo_anual=0.03,
                tasa_inflacion_anual=0.03,
                tasa_apreciacion_propiedad_anual=0.03,
                tasa_crecimiento_ingreso_anual=0.02,
            ),
            'OPTIMISTA': EscenarioMacro(
                nombre='OPTIMISTA',
                tasa_hipotecaria_anual=0.03,
                tasa_plazo_anual=0.04,
                tasa_inflacion_anual=0.02,
                tasa_apreciacion_propiedad_anual=0.05,
                tasa_crecimiento_ingreso_anual=0.03,
            ),
        }

    def get_escenario_macro(self, nombre: str) -> EscenarioMacro:
        """Retorna un escenario macroeconómico."""
        return self._escenarios_macro.get(nombre)

    def escenarios_disponibles(self) -> list[str]:
        """Lista de escenarios disponibles."""
        return list(self._escenarios_macro.keys())
