"""
Formateadores: funciones para formatear salida de datos.
"""


def format_uf(valor: float, decimales: int = 2) -> str:
    """Formatea un valor en UF."""
    return f"UF {valor:,.{decimales}f}"


def format_pct(valor: float, decimales: int = 2) -> str:
    """Formatea un porcentaje."""
    return f"{valor * 100:.{decimales}f}%"


def format_currency_clp(valor_uf: float, usd_per_uf: float = 30) -> str:
    """Convierte UF a CLPy formatea."""
    clp = valor_uf * usd_per_uf
    return f"CLP ${clp:,.0f}"
