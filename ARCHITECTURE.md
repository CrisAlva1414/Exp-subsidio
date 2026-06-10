# Arquitectura del Proyecto: Simulación DS1

## Visión General

Motor financiero determinístico para evaluar qué estrategia (Tramo 2 o Tramo 3 del subsidio DS1) maximiza el patrimonio neto esperado a los 55 años para un Ingeniero Civil Industrial en Santiago.

## Principios de Diseño

1. **Modularidad**: Cada componente tiene una responsabilidad única y bien definida.
2. **Determinístico primero**: Antes de Monte Carlo, árbol de decisiones u optimización.
3. **Datos, no hardcoding**: Toda información viene de CSVs.
4. **Type hints**: Uso de type hints para claridad y validación.
5. **Testing**: Pruebas unitarias para componentes críticos.

## Estructura de Carpetas

```
src/
├── config/
│   └── config.py              # Constantes globales
├── data/
│   └── data_manager.py        # Carga e integración de CSVs
├── models/
│   ├── property.py            # Propiedad inmobiliaria
│   ├── income.py              # Ingresos y proyecciones
│   ├── mortgage.py            # Hipoteca y amortización
│   ├── household.py           # Gastos del hogar
│   ├── ds1.py                 # Parámetros de subsidio
│   └── macro.py               # Escenarios macroeconómicos
├── engines/
│   ├── scenario_engine.py     # Gestión de escenarios
│   ├── mortgage_engine.py     # Tabla de amortización
│   ├── cashflow_engine.py     # Flujos de caja
│   ├── equity_engine.py       # Patrimonio neto
│   ├── decision_engine.py     # Comparación de estrategias
│   └── evaluation_engine.py   # Métricas finales
├── simulations/
│   ├── tramo2_simulation.py   # Simulación Tramo 2
│   └── tramo3_simulation.py   # Simulación Tramo 3
├── evaluation/
│   └── metrics.py             # Funciones de cálculo de métricas
├── utils/
│   ├── validators.py          # Validadores
│   └── formatters.py          # Formateadores de salida
└── main.py                    # Punto de entrada

tests/
├── test_mortgage_engine.py
├── test_cashflow_engine.py
└── test_equity_engine.py

data/                         # CSVs (no bajo control del código)
├── ipc_uf.csv
├── tasas.csv
├── ds1.csv
├── costos_propiedad.csv
├── hogar.csv
├── infraestructura.csv
├── macro_escenarios.csv
├── ici_ingresos.csv
└── mercado_inmobiliario.csv
```

## Flujo de Ejecución

```
main.py
  │
  ├─> DataManager: carga CSVs
  │
  ├─> ScenarioEngine: construye escenarios BASE/PESIMISTA/OPTIMISTA
  │
  ├─> Tramo2Simulation
  │   ├─> MortgageEngine: tabla de amortización
  │   ├─> CashflowEngine: flujos mensuales
  │   ├─> EquityEngine: patrimonio mes a mes
  │   └─> EvaluationEngine: métricas finales
  │
  ├─> Tramo3Simulation
  │   ├─> MortgageEngine
  │   ├─> CashflowEngine
  │   ├─> EquityEngine
  │   └─> EvaluationEngine
  │
  └─> DecisionEngine: comparación y recomendación
```

## Modelos Clave

### Propiedad
- Valor de compra (UF)
- Tasas de apreciación por escenario
- Cálculo de valor futuro y plusvalía

### Ingreso
- Ingreso bruto inicial (UF)
- Crecimiento anual por escenario
- Cálculo de ingreso neto (post-impuestos)

### Hipoteca
- Monto inicial, plazo, tasa
- Cálculo de dividendo (cuota fija)
- Método de amortización francesa

### Hogar
- Gastos base por categoría
- Crecimiento de gastos
- Desglose mensual

### DS1
- Características de Tramo 2 y Tramo 3
- Validación de elegibilidad
- Cálculo de monto a financiar

### EscenarioMacro
- Tasa hipotecaria, inflación
- Apreciación de propiedad
- Crecimiento de ingresos

## Engines

### ScenarioEngine
Construye y gestiona escenarios. Actualmente placeholders; será reemplazado con datos de `macro_escenarios.csv`.

### MortgageEngine
Construye tabla de amortización de 360 meses con:
- Dividendo (cuota fija)
- Interés (decreciente)
- Amortización (creciente)
- Saldo insoluto

### CashflowEngine
Calcula mes a mes:
- Ingreso bruto y líquido
- Dividendo y gastos
- Flujo libre y ahorro acumulado
- Validación de restricción dividendo <= 30%

### EquityEngine
Proyecta patrimonio neto = Valor propiedad + Ahorros - Saldo deuda

### EvaluationEngine
Calcula:
- Patrimonio a 5, 10, 20, 30 años
- VAN y TIR (simplificados)
- Métricas de estrés financiero

### DecisionEngine
Compara Tramo 2 vs Tramo 3 y propone estrategia óptima.

## Fases de Implementación

- **FASE 1**: ✓ Estructura y placeholders
- **FASE 2**: DataManager completo
- **FASE 3**: Modelos y ScenarioEngine
- **FASE 4**: MortgageEngine
- **FASE 5**: CashflowEngine
- **FASE 6**: EquityEngine
- **FASE 7**: Simulaciones (Tramo2, Tramo3)
- **FASE 8**: EvaluationEngine y DecisionEngine
