"""
Validadores: funciones para validar datos e hipótesis.
"""

from src.models.ds1 import SubsidioDS1
from src.models.mortgage import Hipoteca


def validar_elegibilidad_subsidio(
    subsidio: SubsidioDS1,
    valor_propiedad_uf: float,
    ingreso_liquido_mensual_uf: float,
) -> tuple[bool, list[str]]:
    """
    Valida elegibilidad para un subsidio.

    Returns:
        Tupla (es_elegible, lista_de_errores)
    """
    errores = []

    if not (
        subsidio.rango_precio_minimo_uf
        <= valor_propiedad_uf
        <= subsidio.rango_precio_maximo_uf
    ):
        errores.append(
            f"Precio fuera de rango [{subsidio.rango_precio_minimo_uf}, "
            f"{subsidio.rango_precio_maximo_uf}]"
        )

    ingreso_anual = ingreso_liquido_mensual_uf * 12
    if not (
        subsidio.rango_ingreso_minimo_uf
        <= ingreso_anual
        <= subsidio.rango_ingreso_maximo_uf
    ):
        errores.append(
            f"Ingreso anual fuera de rango "
            f"[{subsidio.rango_ingreso_minimo_uf}, {subsidio.rango_ingreso_maximo_uf}]"
        )

    return (len(errores) == 0, errores)


def validar_hipoteca(hipoteca: Hipoteca) -> tuple[bool, list[str]]:
    """Valida parámetros de hipoteca."""
    errores = []

    if hipoteca.monto_inicial_uf <= 0:
        errores.append("Monto inicial debe ser positivo")

    if hipoteca.plazo_meses <= 0:
        errores.append("Plazo debe ser positivo")

    if hipoteca.plazo_meses > 360:  # 30 años
        errores.append("Plazo no puede exceder 30 años")

    return (len(errores) == 0, errores)
