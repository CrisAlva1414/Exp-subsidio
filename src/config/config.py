"""
Configuración global del modelo de proyección inmobiliaria.

Define constantes, parámetros y escenarios para la simulación
del subsidio DS1 (Tramo 2 y Tramo 3).
"""

from dataclasses import dataclass
from pathlib import Path
from enum import Enum

# ============================================================================
# Rutas
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"

# ============================================================================
# Demografía
# ============================================================================

EDAD_COMPRA = 25
EDAD_FINAL = 55
HORIZONTE_MESES = 360  # 30 años * 12 meses

# ============================================================================
# Hipoteca
# ============================================================================

PLAZO_HIPOTECARIO_ANOS = 20
PLAZO_HIPOTECARIO_MESES = PLAZO_HIPOTECARIO_ANOS * 12

MAX_ENDEUDAMIENTO_PCT = 80.0  # % del valor propiedad
MIN_ENDEUDAMIENTO_PCT = 20.0  # % del valor propiedad (requerimiento mínimo)

# ============================================================================
# Restricciones de Cash Flow
# ============================================================================

MAX_DIVIDENDO_PCT_INGRESO = 30.0  # Dividendo <= 30% del ingreso líquido

# ============================================================================
# Subsidios DS1
# ============================================================================


class TramoSubsidio(str, Enum):
    """Categorización de tramos del subsidio DS1."""
    TRAMO_2 = "TRAMO_2"
    TRAMO_3 = "TRAMO_3"


# ============================================================================
# Escenarios
# ============================================================================


class EscenarioIngreso(str, Enum):
    """Escenarios para proyección de ingresos."""
    PESIMISTA = "PESIMISTA"
    BASE = "BASE"
    OPTIMISTA = "OPTIMISTA"


class EscenarioMacro(str, Enum):
    """Escenarios macroeconómicos."""
    PESIMISTA = "PESIMISTA"
    BASE = "BASE"
    OPTIMISTA = "OPTIMISTA"


# ============================================================================
# Producto inmobiliario
# ============================================================================

UBICACION = "Gran Santiago"
TIPO_PROPIEDAD = "Casa/Departamento"

# ============================================================================
# Gasto mensual estimado (placeholder - será cargado de datos)
# ============================================================================

@dataclass
class GastosHogar:
    """Gastos mensuales del hogar (UF)."""
    servicios_basicos: float = 0.0      # Agua, luz, gas
    mantenimiento: float = 0.0          # Reparaciones
    seguros: float = 0.0                # Seguros de propiedad
    administracion: float = 0.0         # Gastos comunes (si aplica)
    otros: float = 0.0                  # Otros gastos

    @property
    def total_mensual_uf(self) -> float:
        """Total gastos mensuales en UF."""
        return (
            self.servicios_basicos
            + self.mantenimiento
            + self.seguros
            + self.administracion
            + self.otros
        )


# ============================================================================
# Parámetros de optimización
# ============================================================================

TASA_DESCUENTO_ANUAL = 0.05  # 5% anual (TIR esperada del dinero)
TASA_INFLACION_BASE_ANUAL = 0.03  # 3% anual (para deflactar valores)

# ============================================================================
# Monte Carlo (futuro)
# ============================================================================

SIMULACIONES_MONTE_CARLO = 1000
RANDOM_SEED = 42
