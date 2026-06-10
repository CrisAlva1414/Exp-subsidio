"""
simulation_core.py: implementación completa de las simulaciones Tramo 2 y Tramo 3.

Conecta todos los engines con parámetros reales del DS1 chileno.
Reemplaza los placeholders de tramo2_simulation.py y tramo3_simulation.py
"""

from datetime import datetime
import numpy as np
import pandas as pd
from dataclasses import dataclass, field

from src.models.income import Ingreso
from src.models.mortgage import Hipoteca
from src.models.property import Propiedad
from src.models.household import Hogar
from src.models.ds1 import SubsidioDS1, TramoSubsidio
from src.models.ds1_params import get_subsidio_tramo2, get_subsidio_tramo3, PerfilICI


# ============================================================================
# Parámetros macro por escenario (tasas hipotecarias Chile 2024)
# ============================================================================

TASAS_HIPOTECARIAS = {
    'PESIMISTA': 0.055,   # 5.5% anual — mercado tenso
    'BASE':      0.045,   # 4.5% anual — condición promedio 2024
    'OPTIMISTA': 0.035,   # 3.5% anual — ciclo de baja TPM
}

TASAS_APRECIACION = {
    'PESIMISTA': 0.01,
    'BASE':      0.03,
    'OPTIMISTA': 0.05,
}


@dataclass
class ResultadoSimulacion:
    """Resultado completo de una simulación."""
    tramo: str
    escenario_ingreso: str
    escenario_macro: str

    # Parámetros de entrada
    valor_propiedad_uf: float = 0.0
    monto_subsidio_uf: float = 0.0
    ahorro_inicial_uf: float = 0.0
    monto_hipoteca_uf: float = 0.0
    dividendo_mensual_uf: float = 0.0
    tasa_hipotecaria_anual: float = 0.0

    # DataFrames
    df_amortizacion: pd.DataFrame = field(default_factory=pd.DataFrame)
    df_cashflow: pd.DataFrame = field(default_factory=pd.DataFrame)
    df_equity: pd.DataFrame = field(default_factory=pd.DataFrame)

    # Métricas clave
    metricas: dict = field(default_factory=dict)

    # Elegibilidad
    es_elegible: bool = True
    errores_elegibilidad: list = field(default_factory=list)


class SimulacionDS1:
    """
    Motor principal de simulación para Tramo 2 o Tramo 3 del DS1.
    
    Implementa la lógica completa que los placeholders dejaban pendiente.
    """

    def __init__(
        self,
        subsidio: SubsidioDS1,
        perfil: PerfilICI,
        mortgage_engine,
        cashflow_engine,
        equity_engine,
        evaluation_engine,
    ):
        self.subsidio = subsidio
        self.perfil = perfil
        self.mortgage_engine = mortgage_engine
        self.cashflow_engine = cashflow_engine
        self.equity_engine = equity_engine
        self.evaluation_engine = evaluation_engine

    def run(
        self,
        escenario_ingreso: str = "BASE",
        escenario_macro: str = "BASE",
        valor_propiedad_uf: float = None,
    ) -> ResultadoSimulacion:
        """
        Ejecuta simulación completa de 30 años.
        
        Args:
            escenario_ingreso: PESIMISTA / BASE / OPTIMISTA
            escenario_macro: PESIMISTA / BASE / OPTIMISTA
            valor_propiedad_uf: Valor de la propiedad. Si None, usa el punto
                                medio del rango del tramo.
        
        Returns:
            ResultadoSimulacion con todos los DataFrames y métricas.
        """
        resultado = ResultadoSimulacion(
            tramo=self.subsidio.tramo.value,
            escenario_ingreso=escenario_ingreso,
            escenario_macro=escenario_macro,
        )

        # 1. Determinar valor propiedad
        if valor_propiedad_uf is None:
            valor_propiedad_uf = (
                self.subsidio.rango_precio_minimo_uf
                + self.subsidio.rango_precio_maximo_uf
            ) / 2.0
        resultado.valor_propiedad_uf = valor_propiedad_uf

        # 2. Calcular financiamiento
        ahorro_inicial = self.perfil.ahorro_inicial_uf
        monto_subsidio = self.subsidio.monto_subsidio_uf
        
        # Monto hipoteca = Precio - Subsidio - Ahorro (sin exceder 80% del precio)
        monto_hipoteca = valor_propiedad_uf - monto_subsidio - ahorro_inicial
        max_hipoteca = valor_propiedad_uf * (self.subsidio.max_endeudamiento_pct / 100.0)
        monto_hipoteca = min(monto_hipoteca, max_hipoteca)
        monto_hipoteca = max(monto_hipoteca, 0.0)

        resultado.monto_subsidio_uf = monto_subsidio
        resultado.ahorro_inicial_uf = ahorro_inicial
        resultado.monto_hipoteca_uf = monto_hipoteca

        # 3. Crear objetos del modelo
        ingreso = Ingreso(
            ingreso_bruto_mes_0_uf=self.perfil.ingreso_bruto_inicial_uf,
            tasa_crecimiento_anual=self.perfil.tasas_crecimiento,
            tasa_impuesto_marginal_nominal=self.perfil.tasa_impuesto,
        )

        tasa_hipotecaria = TASAS_HIPOTECARIAS[escenario_macro]
        resultado.tasa_hipotecaria_anual = tasa_hipotecaria
        
        hipoteca = Hipoteca(
            monto_inicial_uf=monto_hipoteca,
            plazo_meses=self.subsidio.plazo_hipoteca_meses,
            tasa_anual_nominal={
                'PESIMISTA': TASAS_HIPOTECARIAS['PESIMISTA'],
                'BASE':      TASAS_HIPOTECARIAS['BASE'],
                'OPTIMISTA': TASAS_HIPOTECARIAS['OPTIMISTA'],
            },
            fecha_inicio=datetime(2024, 1, 1),
        )

        propiedad = Propiedad(
            valor_compra_uf=valor_propiedad_uf,
            fecha_compra=datetime(2024, 1, 1),
            tasas_apreciacion_anual=TASAS_APRECIACION,
        )

        hogar = Hogar(
            gastos_mensuales_base_uf={
                'servicios_basicos': 0.6,   # ~$46k CLP
                'mantenimiento':     0.3,
                'seguros':           0.25,
                'administracion':    0.0,
                'otros':             0.2,
            },
            tasa_crecimiento_gasto_anual=0.02,
        )

        # 4. Tabla de amortización
        df_amort = self.mortgage_engine.build_amortization_table(
            hipoteca, escenario_macro
        )
        resultado.dividendo_mensual_uf = hipoteca.dividendo_uf(escenario_macro)
        resultado.df_amortizacion = df_amort

        # 5. Construir lista dividendos mensuales (30 años = 360 meses)
        # Dividendo durante el plazo hipotecario, 0 después
        dividendos_mensuales = []
        for mes in range(361):
            if mes == 0:
                # Mes 0: cierre de la compra (desembolso inicial)
                dividendos_mensuales.append(0.0)
            elif mes <= self.subsidio.plazo_hipoteca_meses:
                dividendos_mensuales.append(hipoteca.dividendo_uf(escenario_macro))
            else:
                dividendos_mensuales.append(0.0)

        # 6. Cashflow
        df_cf = self.cashflow_engine.build_cashflow_monthly(
            ingreso, hogar, dividendos_mensuales,
            escenario_ingreso, escenario_macro
        )
        resultado.df_cashflow = df_cf

        # 7. Equity — construir lista de saldos hipotecarios para 361 meses
        saldos_hipotecarios = [monto_hipoteca]  # mes 0: deuda inicial
        for mes in range(1, 361):
            if mes <= len(df_amort):
                saldos_hipotecarios.append(
                    df_amort.iloc[mes - 1]['saldo_insoluto']
                )
            else:
                saldos_hipotecarios.append(0.0)

        ahorros_acumulados = df_cf['ahorro_acumulado'].tolist()

        df_eq = self.equity_engine.build_equity_monthly(
            propiedad, saldos_hipotecarios, ahorros_acumulados, escenario_macro
        )
        resultado.df_equity = df_eq

        # 8. Métricas
        resultado.metricas = self._calcular_metricas(
            resultado, df_amort, df_cf, df_eq, hipoteca, escenario_macro
        )

        # 9. Elegibilidad
        ingreso_liquido_mes0 = ingreso.ingreso_liquido_uf(0, escenario_ingreso)
        elegible, errores = self.subsidio.es_elegible(
            valor_propiedad_uf, ingreso_liquido_mes0
        ), []
        resultado.es_elegible = self.subsidio.es_elegible(
            valor_propiedad_uf, ingreso_liquido_mes0
        )

        return resultado

    def _calcular_metricas(
        self,
        resultado: ResultadoSimulacion,
        df_amort: pd.DataFrame,
        df_cf: pd.DataFrame,
        df_eq: pd.DataFrame,
        hipoteca: Hipoteca,
        escenario_macro: str,
    ) -> dict:
        """Calcula todas las métricas de evaluación."""
        m = {}

        # ---- Patrimonio a hitos ----
        for anos in [5, 10, 15, 20, 25, 30]:
            mes = anos * 12
            if mes < len(df_eq):
                m[f'patrimonio_{anos}a_uf'] = df_eq.iloc[mes]['patrimonio_neto']
                m[f'valor_prop_{anos}a_uf'] = df_eq.iloc[mes]['valor_propiedad']
                m[f'deuda_{anos}a_uf'] = df_eq.iloc[mes]['saldo_deuda']
        
        m['patrimonio_final_uf'] = df_eq.iloc[-1]['patrimonio_neto']

        # ---- Cashflow ----
        m['dividendo_mensual_uf'] = resultado.dividendo_mensual_uf
        m['ratio_dividendo_ingreso_inicial'] = (
            resultado.dividendo_mensual_uf
            / df_cf.iloc[1]['ingreso_liquido']
            if df_cf.iloc[1]['ingreso_liquido'] > 0 else 0.0
        )
        m['max_ratio_dividendo'] = df_cf['ratio_dividendo_ingreso'].max()
        m['meses_flujo_negativo'] = int((df_cf['flujo_libre'] < 0).sum())
        m['flujo_libre_minimo_uf'] = df_cf['flujo_libre'].min()
        m['flujo_libre_promedio_uf'] = df_cf['flujo_libre'].mean()

        # ---- Costo total hipoteca ----
        total_pagado = resultado.dividendo_mensual_uf * hipoteca.plazo_meses
        m['total_pagado_hipoteca_uf'] = total_pagado
        m['costo_financiero_uf'] = total_pagado - resultado.monto_hipoteca_uf
        m['ratio_costo_valor'] = total_pagado / resultado.valor_propiedad_uf

        # ---- VAN (inversión en inmueble vs alquiler) ----
        # Flujos libres descontados al 5% anual
        flujos = df_cf['flujo_libre'].tolist()
        m['van_5pct_uf'] = _calculate_van(flujos, tasa_descuento_anual=0.05)

        # ---- ROI sobre desembolso inicial ----
        desembolso_inicial = resultado.ahorro_inicial_uf
        plusvalia_final = df_eq.iloc[-1]['plusvalia']
        m['roi_plusvalia_pct'] = (
            (plusvalia_final / desembolso_inicial) * 100
            if desembolso_inicial > 0 else 0.0
        )

        # ---- Punto de equilibrio (mes en que patrimonio neto > 0) ----
        positivos = df_eq[df_eq['patrimonio_neto'] > 0]
        m['mes_breakeven'] = int(positivos.index[0]) if len(positivos) > 0 else -1

        # ---- Liberación de flujo (mes en que acaba hipoteca) ----
        m['mes_fin_hipoteca'] = hipoteca.plazo_meses
        m['flujo_libre_post_hipoteca_uf'] = (
            df_cf[df_cf['mes'] > hipoteca.plazo_meses]['flujo_libre'].mean()
        )

        return m


# ============================================================================
# Utilidades financieras
# ============================================================================

def _calculate_van(
    flujos: list[float],
    tasa_descuento_anual: float = 0.05,
) -> float:
    """VAN de una serie de flujos mensuales."""
    tasa_mensual = (1 + tasa_descuento_anual) ** (1 / 12) - 1
    return sum(
        flujo / ((1 + tasa_mensual) ** mes)
        for mes, flujo in enumerate(flujos)
    )