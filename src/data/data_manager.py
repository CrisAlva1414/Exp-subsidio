"""
DataManager: carga e integración de datos desde CSVs.

Responsable de:
- Cargar todos los CSVs
- Validar integridad
- Exponer interfaces limpias para acceso a datos
"""

from pathlib import Path
import pandas as pd
from src.config.config import DATA_DIR


class DataManager:
    """Gestor centralizado de datos."""

    def __init__(self, data_dir: Path = DATA_DIR):
        self.data_dir = data_dir
        self._data = {}
        self._load_all()

    def _load_all(self):
        """Carga todos los CSVs disponibles."""
        csv_files = {
            'ipc_uf': 'ipc_uf.csv',
            'tasas': 'tasas.csv',
            'ds1': 'ds1.csv',
            'costos_propiedad': 'costos_propiedad.csv',
            'hogar': 'hogar.csv',
            'infraestructura': 'infraestructura.csv',
            'macro_escenarios': 'macro_escenarios.csv',
            'ici_ingresos': 'ici_ingresos.csv',
            'mercado_inmobiliario': 'mercado_inmobiliario.csv',
        }

        for key, filename in csv_files.items():
            filepath = self.data_dir / filename
            if filepath.exists():
                try:
                    self._data[key] = pd.read_csv(filepath)
                    print(f"✓ Cargado: {filename}")
                except Exception as e:
                    print(f"✗ Error cargando {filename}: {e}")
            else:
                print(f"⚠ No encontrado: {filename}")

    def get_df(self, key: str) -> pd.DataFrame:
        """Retorna un DataFrame por clave."""
        return self._data.get(key, pd.DataFrame())

    def get_ipc_uf(self) -> pd.DataFrame:
        """Retorna datos de IPC y UF."""
        return self.get_df('ipc_uf')

    def get_tasas(self) -> pd.DataFrame:
        """Retorna datos de tasas de interés."""
        return self.get_df('tasas')

    def get_ds1(self) -> pd.DataFrame:
        """Retorna datos del subsidio DS1."""
        return self.get_df('ds1')

    def get_costos_propiedad(self) -> pd.DataFrame:
        """Retorna costos de propiedad."""
        return self.get_df('costos_propiedad')

    def get_hogar(self) -> pd.DataFrame:
        """Retorna gastos del hogar."""
        return self.get_df('hogar')

    def get_infraestructura(self) -> pd.DataFrame:
        """Retorna datos de infraestructura."""
        return self.get_df('infraestructura')

    def get_macro_escenarios(self) -> pd.DataFrame:
        """Retorna escenarios macroeconómicos."""
        return self.get_df('macro_escenarios')

    def get_ici_ingresos(self) -> pd.DataFrame:
        """Retorna datos de ingresos para ICI."""
        return self.get_df('ici_ingresos')

    def get_mercado_inmobiliario(self) -> pd.DataFrame:
        """Retorna datos del mercado inmobiliario."""
        return self.get_df('mercado_inmobiliario')

    def summary(self):
        """Imprime un resumen de datos cargados."""
        print("\n" + "="*60)
        print("RESUMEN DE DATOS CARGADOS")
        print("="*60)
        for key, df in self._data.items():
            print(f"{key:.<30} {df.shape[0]:>5} rows × {df.shape[1]:>2} cols")
        print("="*60 + "\n")
