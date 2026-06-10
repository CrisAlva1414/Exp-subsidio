"""
data_driven_runner.py: simulación completamente calibrada desde CSVs reales.

Diferencias clave respecto al runner.py anterior (que usaba parámetros hardcodeados):

1. INGRESOS: calibrados desde ici_ingresos.csv (Mi Futuro MINEDUC 2024)
   - Año 0 base: 1.660.000 CLP ~ 38.5 UF (UF mayo-2025: 43.137 CLP)
   - Curva real por años de experiencia, no crecimiento exponencial constante

2. DS1: parámetros reales desde ds1.csv
   - Tramo 2: max 1.600 UF, subsidio promedio 450 UF (rango 200-650)
   - Tramo 3: max 2.200 UF, subsidio promedio 325 UF (rango 250-400)

3. MACRO: tasas desde macro_escenarios.csv + tasas.csv reales BCCh
   - Tasa hipotecaria actual: 4.0% (junio 2025, tasas.csv)
   - Proyección por período 2025-2035 / 2035-2055

4. MERCADO: plusvalías diferenciadas por zona desde mercado_inmobiliario.csv

5. GASTOS PROPIEDAD: desde costos_propiedad.csv (gastos comunes + seguro + contrib.)

6. DEMOGRAFÍA: ajuste de gastos según probabilidad pareja/hijos desde hogar.csv

Uso:
    python data_driven_runner.py
    python data_driven_runner.py --escenario BASE --zona La_Florida
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import argparse
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from tabulate import tabulate


# ============================================================================
# Carga de datos reales
# ============================================================================

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def load_csv(name):
    path = os.path.join(DATA_DIR, name)
    if os.path.exists(path):
        return pd.read_csv(path)
    print(f"⚠ No encontrado: {name}")
    return pd.DataFrame()


# ============================================================================
# Calibración desde CSVs
# ============================================================================

def get_uf_actual() -> float:
    """UF actual desde ipc_uf.csv."""
    df = load_csv('ipc_uf.csv')
    if df.empty:
        return 43136.62
    return float(df.sort_values('fecha').iloc[-1]['uf_clp'])


def get_tasa_hipotecaria_actual() -> float:
    """Tasa hipotecaria más reciente desde tasas.csv."""
    df = load_csv('tasas.csv')
    if df.empty:
        return 0.04
    return float(df.sort_values('fecha').iloc[-1]['tasa_hipotecaria_uf_pct']) / 100.0


def get_macro_parametros(escenario: str) -> dict:
    """
    Parámetros macro desde macro_escenarios.csv.
    Promedia los dos horizontes (2025-2035 y 2035-2055) con ponderación 1:2.
    """
    df = load_csv('macro_escenarios.csv')
    if df.empty:
        defaults = {
            'pesimista': {'tasa_hipotecaria': 0.055, 'crec_salarios': 0.010, 'crec_vivienda': -0.005},
            'base':      {'tasa_hipotecaria': 0.040, 'crec_salarios': 0.025, 'crec_vivienda': 0.020},
            'optimista': {'tasa_hipotecaria': 0.032, 'crec_salarios': 0.040, 'crec_vivienda': 0.040},
        }
        return defaults.get(escenario.lower(), defaults['base'])

    esc_rows = df[df['escenario'] == escenario.lower()]
    if esc_rows.empty:
        esc_rows = df[df['escenario'] == 'base']

    # Ponderación: 10 años (2025-2035) + 20 años (2035-2055) = 30 años
    row1 = esc_rows.iloc[0]  # 2025-2035
    row2 = esc_rows.iloc[1] if len(esc_rows) > 1 else row1  # 2035-2055

    tasa_hip = (row1['tasa_hipotecaria_uf_pct'] * 10 + row2['tasa_hipotecaria_uf_pct'] * 20) / 30 / 100
    crec_sal = (row1['crecimiento_salarios_real_pct'] * 10 + row2['crecimiento_salarios_real_pct'] * 20) / 30 / 100
    crec_viv = (row1['crecimiento_precios_vivienda_real_pct'] * 10 + row2['crecimiento_precios_vivienda_real_pct'] * 20) / 30 / 100

    return {
        'tasa_hipotecaria': tasa_hip,
        'crec_salarios': crec_sal,
        'crec_vivienda': crec_viv,
        'row1': row1,
        'row2': row2,
    }


def get_ingreso_ici_curva(escenario: str, uf_clp: float) -> list:
    """
    Curva de ingreso real desde ici_ingresos.csv.
    Retorna ingreso bruto mensual en UF para cada mes 0..360.
    El ingreso está anclado en datos MiFuturo (CLP), convertido a UF con UF actual.
    """
    df = load_csv('ici_ingresos.csv')
    col = {
        'pesimista': 'ingreso_pesimista_clp',
        'base':      'ingreso_base_clp',
        'optimista': 'ingreso_optimista_clp',
    }.get(escenario.lower(), 'ingreso_base_clp')

    if df.empty or col not in df.columns:
        # Fallback: 22 UF base con crecimiento 2% anual
        return [22.0 * ((1.02 / 12 + 1) ** m) for m in range(361)]

    # Interpolación para todos los años 0..30
    años_data = df['años_experiencia'].tolist()
    ingresos_clp = df[col].tolist()

    ingresos_uf_por_mes = []
    for mes in range(361):
        anos_exp = mes / 12
        # Interpolación lineal
        ingreso_clp = np.interp(anos_exp, años_data, ingresos_clp)
        ingresos_uf_por_mes.append(ingreso_clp / uf_clp)

    return ingresos_uf_por_mes


def get_ds1_params(tramo_num: int) -> dict:
    """Parámetros DS1 reales desde ds1.csv."""
    df = load_csv('ds1.csv')
    if df.empty:
        if tramo_num == 2:
            return {'max_uf': 1600, 'subsidio_prom': 450, 'subsidio_min': 200, 'subsidio_max': 650, 'ahorro_min': 40}
        else:
            return {'max_uf': 2200, 'subsidio_prom': 325, 'subsidio_min': 250, 'subsidio_max': 400, 'ahorro_min': 80}

    tramo_key = f'Tramo_{tramo_num}'
    row = df[df['tramo'] == tramo_key]
    if row.empty:
        return get_ds1_params(tramo_num)  # fallback
    r = row.iloc[0]
    return {
        'max_uf': float(r['vivienda_max_uf_zona_normal']),
        'subsidio_prom': float(r['subsidio_promedio_uf']),
        'subsidio_min': float(r['subsidio_min_uf']),
        'subsidio_max': float(r['subsidio_max_uf']),
        'ahorro_min': float(r['ahorro_min_uf']),
    }


def get_plusvalia_zona(zona: str, escenario: str) -> float:
    """
    Tasa anual de apreciación real desde mercado_inmobiliario.csv.
    Usa la plusvalía 10a observada como referencia y ajusta por escenario macro.
    """
    df = load_csv('mercado_inmobiliario.csv')
    macro = get_macro_parametros(escenario)
    crec_base = macro['crec_vivienda']  # ya es decimal anual

    # Si no hay datos de mercado, usar solo el macro
    if df.empty:
        return crec_base

    # Buscar la zona en el CSV
    row = df[df['comuna'].str.lower().str.replace(' ', '') == zona.lower().replace(' ', '')]
    if row.empty:
        # Tomar promedio de comunas accesibles DS1 (excluye Providencia)
        comunas_ds1 = df[~df['comuna'].isin(['Providencia'])]
        if not comunas_ds1.empty and 'plusvalia_10a_pct' in df.columns:
            plus10a = comunas_ds1['plusvalia_10a_pct'].dropna().mean()
            tasa_anual_historica = (1 + plus10a / 100) ** (1 / 10) - 1
            # Promedio entre histórico y macro-proyectado
            return (tasa_anual_historica + crec_base) / 2
        return crec_base

    r = row.iloc[0]
    if 'plusvalia_10a_pct' in r and pd.notna(r['plusvalia_10a_pct']):
        tasa_anual_historica = (1 + float(r['plusvalia_10a_pct']) / 100) ** (1 / 10) - 1
        return (tasa_anual_historica + crec_base) / 2

    return crec_base


def get_gastos_propiedad_uf(tramo_num: int, valor_prop_uf: float) -> dict:
    """Gastos mensuales reales de la propiedad desde costos_propiedad.csv."""
    df = load_csv('costos_propiedad.csv')
    tipo = f'Departamento_DS1_tramo{tramo_num}_{"50m2" if tramo_num == 2 else "55m2"}'

    if df.empty or 'tipo_propiedad' not in df.columns:
        return {'gastos_comunes': 2.0, 'seguro': 1.0/12, 'contribuciones': 0.0, 'mantencion': valor_prop_uf * 0.008 / 12}

    row = df[df['tipo_propiedad'] == tipo]
    if row.empty:
        row = df.iloc[min(tramo_num - 2, len(df) - 1):tramo_num - 1]

    if row.empty:
        return {'gastos_comunes': 2.0, 'seguro': 1.0/12, 'contribuciones': 0.0, 'mantencion': valor_prop_uf * 0.008 / 12}

    r = row.iloc[0]
    return {
        'gastos_comunes': float(r.get('gastos_comunes_uf_mes', 2.0)),
        'seguro': float(r.get('seguro_anual_uf', 1.0)) / 12,
        'contribuciones': float(r.get('contribuciones_anual_uf', 0.0)) / 12,
        'mantencion': valor_prop_uf * float(r.get('mantencion_anual_pct_valor_propiedad', 0.8)) / 100 / 12,
    }


def get_gastos_hogar_por_edad(edad: float) -> float:
    """
    Ajuste de gastos básicos del hogar según probabilidad de pareja/hijos (hogar.csv).
    Base: 0.8 UF/mes (soltero). Escala hasta ~2.0 UF con familia.
    """
    df = load_csv('hogar.csv')
    if df.empty:
        return 0.8

    edades = df['edad'].tolist()
    personas = df['personas_hogar_promedio'].tolist()
    personas_interp = np.interp(edad, edades, personas)
    # Base 0.5 UF por persona básica (alimentos+transporte)
    return max(0.6, personas_interp * 0.5)


# ============================================================================
# Motor de simulación calibrado
# ============================================================================

@dataclass
class ResultadoCalibrado:
    tramo: int
    escenario: str
    zona: str
    uf_clp: float

    valor_propiedad_uf: float = 0.0
    subsidio_uf: float = 0.0
    ahorro_inicial_uf: float = 0.0
    hipoteca_uf: float = 0.0
    dividendo_mensual_uf: float = 0.0
    tasa_hipotecaria: float = 0.0

    df_amort: pd.DataFrame = field(default_factory=pd.DataFrame)
    df_cashflow: pd.DataFrame = field(default_factory=pd.DataFrame)
    df_equity: pd.DataFrame = field(default_factory=pd.DataFrame)
    metricas: dict = field(default_factory=dict)


def run_simulacion_calibrada(
    tramo_num: int,
    escenario: str,
    zona: str = 'La Florida',
    ahorro_inicial_uf: float = 80.0,
    fraccion_precio: float = 0.85,  # 85% del máximo del tramo (punto realista)
) -> ResultadoCalibrado:
    """
    Simulación completamente calibrada desde CSVs.

    Args:
        tramo_num: 2 o 3
        escenario: BASE / PESIMISTA / OPTIMISTA
        zona: comuna de compra (afecta plusvalía)
        ahorro_inicial_uf: ahorro acumulado al comprar
        fraccion_precio: qué fracción del máximo del tramo se compra
    """
    # ── Datos base ──────────────────────────────────────────────────────────
    uf_clp = get_uf_actual()
    macro = get_macro_parametros(escenario)
    ds1 = get_ds1_params(tramo_num)
    tasa_hip_actual = get_tasa_hipotecaria_actual()

    # Para escenarios, ajustar desde la tasa actual (4.0% junio 2025)
    # Las tasas macro son promedios de largo plazo; para el escenario BASE
    # usamos la tasa actual como punto de partida
    tasa_hipotecaria = macro['tasa_hipotecaria']

    r = ResultadoCalibrado(
        tramo=tramo_num,
        escenario=escenario,
        zona=zona,
        uf_clp=uf_clp,
    )

    # ── Precio propiedad ────────────────────────────────────────────────────
    valor_prop = ds1['max_uf'] * fraccion_precio
    r.valor_propiedad_uf = round(valor_prop, 1)

    # ── Subsidio (promedio del tramo) ───────────────────────────────────────
    subsidio = ds1['subsidio_prom']
    r.subsidio_uf = subsidio

    # ── Hipoteca ─────────────────────────────────────────────────────────────
    r.ahorro_inicial_uf = ahorro_inicial_uf
    hipoteca_bruta = valor_prop - subsidio - ahorro_inicial_uf
    max_hip = valor_prop * 0.80
    hipoteca = min(max(hipoteca_bruta, 0), max_hip)
    r.hipoteca_uf = round(hipoteca, 1)
    r.tasa_hipotecaria = tasa_hipotecaria

    # ── Dividendo (amortización francesa) ───────────────────────────────────
    plazo_meses = 240  # 20 años
    r_mensual = (1 + tasa_hipotecaria) ** (1 / 12) - 1
    if r_mensual > 0:
        dividendo = hipoteca * r_mensual * (1 + r_mensual) ** plazo_meses / ((1 + r_mensual) ** plazo_meses - 1)
    else:
        dividendo = hipoteca / plazo_meses
    r.dividendo_mensual_uf = round(dividendo, 2)

    # ── Tabla amortización ──────────────────────────────────────────────────
    saldo = hipoteca
    amort_rows = []
    for mes in range(1, plazo_meses + 1):
        interes = saldo * r_mensual
        amort = dividendo - interes
        saldo = max(saldo - amort, 0)
        amort_rows.append({'mes': mes, 'dividendo': dividendo, 'interes': interes,
                           'amortizacion': amort, 'saldo_insoluto': saldo})
    r.df_amort = pd.DataFrame(amort_rows)

    # ── Curva de ingresos desde ICI data ────────────────────────────────────
    ingresos_brutos_uf = get_ingreso_ici_curva(escenario, uf_clp)

    # Tasa impuesto efectiva por tramo de renta (simplificada)
    # ICI año 0: ~38.5 UF/mes (~$1.66M CLP) → impuesto ~15% efectivo
    # ICI año 30: ~255 UF/mes (~$11M CLP) → impuesto ~25% efectivo
    def tasa_impuesto(ingreso_bruto_uf, uf_clp):
        ingreso_clp = ingreso_bruto_uf * uf_clp
        if ingreso_clp < 1_500_000:   return 0.10
        if ingreso_clp < 3_000_000:   return 0.15
        if ingreso_clp < 6_000_000:   return 0.20
        if ingreso_clp < 12_000_000:  return 0.23
        return 0.27

    # ── Tasas de crecimiento implícitas en la curva CSV ─────────────────────
    # (ya embebidas en get_ingreso_ici_curva via interpolación directa)

    # ── Gastos propiedad desde CSV ───────────────────────────────────────────
    gastos_prop = get_gastos_propiedad_uf(tramo_num, valor_prop)
    gastos_prop_mensual_base = sum(gastos_prop.values())  # ~2.5-3.5 UF/mes

    # ── Tabla cashflow 361 meses ─────────────────────────────────────────────
    cf_rows = []
    ahorro_acc = 0.0
    saldo_deuda = hipoteca  # deuda al inicio

    for mes in range(361):
        edad = 25 + mes / 12
        ingreso_bruto = ingresos_brutos_uf[mes]
        imp = tasa_impuesto(ingreso_bruto, uf_clp)
        ingreso_liq = ingreso_bruto * (1 - imp)

        div = dividendo if 0 < mes <= plazo_meses else 0.0

        # Gastos: propiedad + hogar demográfico + crecimiento por inflación
        factor_inflacion = (1 + 0.03 / 12) ** mes  # 3% anual IPC aprox
        gastos_hogar_var = get_gastos_hogar_por_edad(edad) * factor_inflacion
        gastos_total = gastos_prop_mensual_base * factor_inflacion + gastos_hogar_var

        flujo = ingreso_liq - div - gastos_total
        ahorro_acc += flujo
        ratio_div = div / ingreso_liq if ingreso_liq > 0 else 0.0

        cf_rows.append({
            'mes': mes, 'edad': round(edad, 1),
            'ingreso_bruto': round(ingreso_bruto, 2),
            'ingreso_liquido': round(ingreso_liq, 2),
            'dividendo': round(div, 2),
            'gastos': round(gastos_total, 2),
            'flujo_libre': round(flujo, 2),
            'ahorro_acumulado': round(ahorro_acc, 1),
            'ratio_dividendo_ingreso': round(ratio_div, 4),
        })

    r.df_cashflow = pd.DataFrame(cf_rows)

    # ── Tabla equity 361 meses ───────────────────────────────────────────────
    tasa_apreciacion = get_plusvalia_zona(zona, escenario)
    tasa_apr_mensual = (1 + tasa_apreciacion) ** (1 / 12) - 1

    # Saldos hipotecarios
    saldos_hip = [hipoteca]  # mes 0
    saldo = hipoteca
    for mes in range(1, 361):
        if mes <= plazo_meses:
            idx = mes - 1
            saldo = float(r.df_amort.iloc[idx]['saldo_insoluto'])
        else:
            saldo = 0.0
        saldos_hip.append(saldo)

    eq_rows = []
    for mes in range(361):
        valor_act = valor_prop * (1 + tasa_apr_mensual) ** mes
        plusvalia = valor_act - valor_prop
        ahorro = r.df_cashflow.iloc[mes]['ahorro_acumulado']
        patrimonio = valor_act + ahorro - saldos_hip[mes]
        eq_rows.append({
            'mes': mes,
            'valor_propiedad': round(valor_act, 1),
            'plusvalia': round(plusvalia, 1),
            'saldo_deuda': round(saldos_hip[mes], 1),
            'ahorros': round(ahorro, 1),
            'patrimonio_neto': round(patrimonio, 1),
        })
    r.df_equity = pd.DataFrame(eq_rows)

    # ── Métricas ─────────────────────────────────────────────────────────────
    r.metricas = _calcular_metricas(r, tasa_apreciacion)
    return r


def _calcular_metricas(r: ResultadoCalibrado, tasa_apreciacion: float) -> dict:
    m = {}
    df_eq = r.df_equity
    df_cf = r.df_cashflow

    for anos in [5, 10, 15, 20, 25, 30]:
        mes = anos * 12
        if mes < len(df_eq):
            m[f'patrimonio_{anos}a_uf'] = df_eq.iloc[mes]['patrimonio_neto']
    m['patrimonio_final_uf'] = df_eq.iloc[-1]['patrimonio_neto']

    m['dividendo_uf'] = r.dividendo_mensual_uf
    m['ratio_div_ingreso_ini'] = round(
        r.dividendo_mensual_uf / df_cf.iloc[1]['ingreso_liquido'], 4
    ) if df_cf.iloc[1]['ingreso_liquido'] > 0 else 0.0
    m['max_ratio_div'] = df_cf['ratio_dividendo_ingreso'].max()
    m['meses_flujo_negativo'] = int((df_cf['flujo_libre'] < 0).sum())
    m['flujo_libre_min_uf'] = df_cf['flujo_libre'].min()
    m['flujo_libre_prom_uf'] = round(df_cf['flujo_libre'].mean(), 2)

    total_pagado = r.dividendo_mensual_uf * 240
    m['costo_financiero_uf'] = round(total_pagado - r.hipoteca_uf, 1)

    # VAN al 5% anual
    flujos = df_cf['flujo_libre'].tolist()
    tasa_m = (1.05) ** (1 / 12) - 1
    m['van_5pct_uf'] = round(sum(f / (1 + tasa_m) ** i for i, f in enumerate(flujos)), 0)

    plusvalia_final = df_eq.iloc[-1]['plusvalia']
    m['roi_plusvalia_pct'] = round(plusvalia_final / max(r.ahorro_inicial_uf, 1) * 100, 1)
    m['tasa_apreciacion_anual'] = round(tasa_apreciacion * 100, 2)
    m['uf_clp_ref'] = r.uf_clp

    # Ingreso en mes 0 y mes 360
    m['ingreso_bruto_ini_uf'] = df_cf.iloc[1]['ingreso_bruto']
    m['ingreso_bruto_fin_uf'] = df_cf.iloc[360]['ingreso_bruto']

    return m


# ============================================================================
# Output
# ============================================================================

def fmt_uf(v): return f'UF {v:>10,.1f}'
def fmt_pct(v): return f'{v:.1%}'
def fmt_clp(v, uf): return f'${v * uf:>14,.0f} CLP'


def print_comparacion(r2: ResultadoCalibrado, r3: ResultadoCalibrado):
    m2, m3 = r2.metricas, r3.metricas
    uf = r2.uf_clp

    print(f'\n{"═"*72}')
    print(f'  SIMULACIÓN DS1 CALIBRADA CON DATOS REALES — Escenario {r2.escenario}')
    print(f'  Zona: {r2.zona} | UF: ${uf:,.0f} CLP | Tasa actual: {r2.tasa_hipotecaria:.2%}')
    print(f'{"═"*72}')

    print('\n  ── Estructura de compra ──')
    t = [
        ['Precio propiedad',  fmt_uf(r2.valor_propiedad_uf), fmt_uf(r3.valor_propiedad_uf),
         fmt_clp(r2.valor_propiedad_uf, uf), fmt_clp(r3.valor_propiedad_uf, uf)],
        ['Subsidio DS1',      fmt_uf(r2.subsidio_uf),        fmt_uf(r3.subsidio_uf), '', ''],
        ['Ahorro inicial',    fmt_uf(r2.ahorro_inicial_uf),  fmt_uf(r3.ahorro_inicial_uf), '', ''],
        ['Hipoteca',          fmt_uf(r2.hipoteca_uf),        fmt_uf(r3.hipoteca_uf),
         fmt_clp(r2.hipoteca_uf, uf), fmt_clp(r3.hipoteca_uf, uf)],
        ['Dividendo/mes',     fmt_uf(r2.dividendo_mensual_uf), fmt_uf(r3.dividendo_mensual_uf),
         fmt_clp(r2.dividendo_mensual_uf, uf), fmt_clp(r3.dividendo_mensual_uf, uf)],
        ['Ratio div/ingreso', fmt_pct(m2['ratio_div_ingreso_ini']), fmt_pct(m3['ratio_div_ingreso_ini']), '', ''],
        ['Tasa apreciación',  f'{m2["tasa_apreciacion_anual"]:.2f}%/a', f'{m3["tasa_apreciacion_anual"]:.2f}%/a', '', ''],
    ]
    print(tabulate(t, headers=['', 'TRAMO 2', 'TRAMO 3', 'T2 en CLP', 'T3 en CLP'], tablefmt='simple'))

    print('\n  ── Ingresos ICI (Mi Futuro MINEDUC 2024) ──')
    t2 = [
        ['Ingreso bruto año 0', fmt_uf(m2["ingreso_bruto_ini_uf"]), fmt_clp(m2["ingreso_bruto_ini_uf"], uf)],
        ['Ingreso bruto año 30', fmt_uf(m2["ingreso_bruto_fin_uf"]), fmt_clp(m2["ingreso_bruto_fin_uf"], uf)],
    ]
    print(tabulate(t2, headers=['', 'UF', 'CLP'], tablefmt='simple'))

    print('\n  ── Patrimonio neto proyectado ──')
    t3 = []
    for anos in [5, 10, 15, 20, 25, 30]:
        k = f'patrimonio_{anos}a_uf'
        v2 = m2.get(k, 0)
        v3 = m3.get(k, 0)
        diff = v2 - v3
        win = '◀ T2' if diff > 0 else 'T3 ▶'
        t3.append([f'{anos}a', fmt_uf(v2), fmt_uf(v3), f'{win} {abs(diff):,.0f} UF'])
    print(tabulate(t3, headers=['Horizonte', 'TRAMO 2', 'TRAMO 3', 'Diferencia'], tablefmt='simple'))

    print('\n  ── Riesgo financiero ──')
    t4 = [
        ['Meses flujo negativo',  m2['meses_flujo_negativo'],  m3['meses_flujo_negativo']],
        ['Flujo mínimo (UF/mes)', f'{m2["flujo_libre_min_uf"]:.1f}', f'{m3["flujo_libre_min_uf"]:.1f}'],
        ['Flujo promedio (UF/mes)',f'{m2["flujo_libre_prom_uf"]:.1f}', f'{m3["flujo_libre_prom_uf"]:.1f}'],
        ['VAN flujos al 5%',      f'{m2["van_5pct_uf"]:.0f} UF', f'{m3["van_5pct_uf"]:.0f} UF'],
        ['Costo financiero total',f'{m2["costo_financiero_uf"]:.0f} UF', f'{m3["costo_financiero_uf"]:.0f} UF'],
        ['ROI plusvalía/ahorro',  f'{m2["roi_plusvalia_pct"]:.0f}%', f'{m3["roi_plusvalia_pct"]:.0f}%'],
    ]
    print(tabulate(t4, headers=['Métrica', 'TRAMO 2', 'TRAMO 3'], tablefmt='simple'))

    # Veredicto
    pf2, pf3 = m2['patrimonio_final_uf'], m3['patrimonio_final_uf']
    ganador = 'TRAMO 2' if pf2 >= pf3 else 'TRAMO 3'
    diff_pat = abs(pf2 - pf3)
    riesgo_t3 = m3['ratio_div_ingreso_ini']

    print(f'\n  ── Recomendación ──')
    print(f'  Patrimonio final: T2 = {fmt_uf(pf2)}  |  T3 = {fmt_uf(pf3)}')
    print(f'  Diferencia: {diff_pat:,.0f} UF a favor de {ganador}')
    if riesgo_t3 > 0.30:
        print(f'  ⚠  Tramo 3: ratio dividendo/ingreso inicial = {riesgo_t3:.1%} > 30% recomendado')
    print(f'\n  ► ESTRATEGIA RECOMENDADA: {ganador}')


def run_todos_escenarios(zona='La Florida'):
    print(f'\n{"█"*72}')
    print(f'  DS1 CHILE — SIMULACIÓN CON DATOS REALES (Mi Futuro + BCCh + MINVU)')
    print(f'  ICI · Santiago · 25 años · UF {get_uf_actual():,.0f} CLP · Zona: {zona}')
    print(f'{"█"*72}')

    resumen = []
    for esc in ['PESIMISTA', 'BASE', 'OPTIMISTA']:
        r2 = run_simulacion_calibrada(2, esc, zona)
        r3 = run_simulacion_calibrada(3, esc, zona)
        print_comparacion(r2, r3)
        ganador = 'T2' if r2.metricas['patrimonio_final_uf'] >= r3.metricas['patrimonio_final_uf'] else 'T3'
        resumen.append([
            esc,
            f'{r2.metricas["patrimonio_final_uf"]:,.0f}',
            f'{r3.metricas["patrimonio_final_uf"]:,.0f}',
            f'{r2.metricas["ratio_div_ingreso_ini"]:.1%}',
            f'{r3.metricas["ratio_div_ingreso_ini"]:.1%}',
            ganador,
        ])

    print(f'\n{"═"*72}')
    print('  RESUMEN MULTI-ESCENARIO')
    print(tabulate(resumen,
        headers=['Escenario', 'Pat.T2 (UF)', 'Pat.T3 (UF)', 'Carga T2', 'Carga T3', 'Ganador'],
        tablefmt='simple'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DS1 simulación calibrada con datos reales')
    parser.add_argument('--escenario', choices=['BASE', 'PESIMISTA', 'OPTIMISTA', 'TODOS'], default='TODOS')
    parser.add_argument('--zona', default='La Florida', help='Comuna de compra (afecta plusvalía)')
    args = parser.parse_args()

    if args.escenario == 'TODOS':
        run_todos_escenarios(zona=args.zona)
    else:
        r2 = run_simulacion_calibrada(2, args.escenario, args.zona)
        r3 = run_simulacion_calibrada(3, args.escenario, args.zona)
        print_comparacion(r2, r3)