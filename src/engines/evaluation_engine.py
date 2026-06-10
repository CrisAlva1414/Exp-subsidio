"""
EvaluationEngine: cálculo de métricas de evaluación.

Responsable de:
- Calcular patrimonio a 5, 10, 20, 30 años
- Calcular VAN, TIR, ROI
- Identificar estrés financiero
- Generar reporte final
"""

import pandas as pd
import numpy as np


class EvaluationEngine:
    """Motor de evaluación de resultados."""

    def __init__(self):
        pass

    def calculate_metrics(
        self,
        df_equity: pd.DataFrame,
        df_cashflow: pd.DataFrame,
    ) -> dict:
        """
        Calcula todas las métricas de evaluación.

        Returns:
            Diccionario con métricas clave.
        """
        metrics = {}

        # Patrimonio a hitos
        hitos = {5: 60, 10: 120, 20: 240, 30: 360}
        for anos, meses in hitos.items():
            if meses < len(df_equity):
                metrics[f'patrimonio_{anos}anos'] = df_equity.iloc[meses][
                    'patrimonio_neto'
                ]

        # Patrimonio final
        metrics['patrimonio_final'] = df_equity.iloc[-1]['patrimonio_neto']

        # VAN y TIR (simplificado)
        metrics['van'] = self._calculate_van(df_cashflow)
        metrics['tir'] = self._calculate_tir(df_cashflow)

        # Estrés financiero
        flujos_negativos = (df_cashflow['flujo_libre'] < 0).sum()
        metrics['meses_estres_financiero'] = flujos_negativos

        # Máximo ratio dividendo
        metrics['max_ratio_dividendo'] = df_cashflow[
            'ratio_dividendo_ingreso'
        ].max()

        # Flujo libre mínimo
        metrics['flujo_libre_minimo'] = df_cashflow['flujo_libre'].min()

        return metrics

    def _calculate_van(self, df_cashflow: pd.DataFrame) -> float:
        """VAN simplificado con tasa 5% anual."""
        # Placeholder
        return 0.0

    def _calculate_tir(self, df_cashflow: pd.DataFrame) -> float:
        """TIR simplificada."""
        # Placeholder
        return 0.0
