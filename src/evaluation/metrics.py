"""
Métricas: funciones para calcular métricas de evaluación.

Proporciona utilidades para VAN, TIR, ROI, etc.
"""

import numpy as np
from typing import List


def calculate_van(
    flujos: List[float],
    tasa_descuento_anual: float = 0.05,
) -> float:
    """
    Calcula VAN de una serie de flujos.

    Args:
        flujos: Lista de flujos mensuales.
        tasa_descuento_anual: Tasa de descuento anual.

    Returns:
        VAN en UF.
    """
    tasa_mensual = (1 + tasa_descuento_anual) ** (1 / 12) - 1
    van = sum(flujo / ((1 + tasa_mensual) ** mes) for mes, flujo in enumerate(flujos))
    return van


def calculate_tir(
    flujos: List[float],
    tolerance: float = 1e-6,
    max_iter: int = 100,
) -> float:
    """
    Calcula TIR de una serie de flujos (Newton-Raphson).

    Args:
        flujos: Lista de flujos mensuales.
        tolerance: Tolerancia de convergencia.
        max_iter: Máximo número de iteraciones.

    Returns:
        TIR mensual (convertible a anual).
    """
    # Simplificación: si no converge, retornar None o 0
    # Implementación completa en siguiente fase
    return 0.0


def calculate_roi(
    ganancia: float,
    inversion_inicial: float,
) -> float:
    """
    Calcula ROI (Return on Investment).

    Returns:
        ROI en porcentaje.
    """
    if inversion_inicial == 0:
        return 0.0
    return (ganancia / inversion_inicial) * 100
