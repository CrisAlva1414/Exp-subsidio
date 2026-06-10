"""
Main: punto de entrada principal.

Orquesta todo el flujo de simulación.
"""

from src.data.data_manager import DataManager
from src.engines.scenario_engine import ScenarioEngine
from src.engines.mortgage_engine import MortgageEngine
from src.engines.cashflow_engine import CashflowEngine
from src.engines.equity_engine import EquityEngine
from src.engines.evaluation_engine import EvaluationEngine
from src.engines.decision_engine import DecisionEngine
from src.simulations.tramo2_simulation import Tramo2Simulation
from src.simulations.tramo3_simulation import Tramo3Simulation


def main():
    """Ejecuta flujo completo de simulación."""

    print("\n" + "="*70)
    print("SIMULACIÓN FINANCIERA: SUBSIDIO DS1 (TRAMO 2 vs TRAMO 3)")
    print("Ingeniero Civil Industrial, Santiago, 25-55 años")
    print("="*70)

    # ====================================================================
    # Inicializar gestores
    # ====================================================================

    data_manager = DataManager()
    data_manager.summary()

    scenario_engine = ScenarioEngine(data_manager)
    mortgage_engine = MortgageEngine()
    cashflow_engine = CashflowEngine()
    equity_engine = EquityEngine()
    evaluation_engine = EvaluationEngine()
    decision_engine = DecisionEngine()

    # ====================================================================
    # Simulaciones
    # ====================================================================

    tramo2_sim = Tramo2Simulation(
        data_manager,
        scenario_engine,
        mortgage_engine,
        cashflow_engine,
        equity_engine,
        evaluation_engine,
    )

    tramo3_sim = Tramo3Simulation(
        data_manager,
        scenario_engine,
        mortgage_engine,
        cashflow_engine,
        equity_engine,
        evaluation_engine,
    )

    print("\nEjecutando simulación TRAMO 2...")
    results_tramo2 = tramo2_sim.run('BASE', 'BASE')

    print("Ejecutando simulación TRAMO 3...")
    results_tramo3 = tramo3_sim.run('BASE', 'BASE')

    # ====================================================================
    # Comparación y decisión
    # ====================================================================

    print("\nComparando resultados...")
    comparison = decision_engine.compare_tramos(results_tramo2, results_tramo3)
    recommendation = decision_engine.recommend_strategy(comparison)

    print(f"\nRECOMENDACIÓN: {recommendation}")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
