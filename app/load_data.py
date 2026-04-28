"""
Módulo de carga de datos.
RESPONSABILIDAD EXCLUSIVA: Leer CSVs, limpieza mínima y construir modelo base.
NINGUNA lógica de negocio debe estar aquí.
"""


import pandas as pd
from pathlib import Path

# Ruta dinámica - funciona sin importar dónde ejecutes
BASE_DIR = Path(__file__).resolve().parent.parent

# Carpeta donde se encuentran los archivos CSV
DATA_DIR = BASE_DIR / "data"


def load_csv(filename: str) -> pd.DataFrame:
    """Carga un archivo CSV desde la carpeta de datos del proyecto."""
    return pd.read_csv(DATA_DIR / filename)


def clean_dataframes(
    clientes: pd.DataFrame,
    productos: pd.DataFrame,
    negocios: pd.DataFrame,
    calendario: pd.DataFrame,
    ventas: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Limpia y normaliza los tipos de datos de todos los DataFrames.
    - Convierte fechas a datetime
    - Convierte valores numéricos y rellena nulos con 0
    - Limpia espacios en columnas de texto e IDs
    """

    # Trabajar sobre copias para no modificar los originales
    ventas = ventas.copy()
    calendario = calendario.copy()
    negocios = negocios.copy()
    clientes = clientes.copy()
    productos = productos.copy()

    # Convertir columnas de fecha a datetime (errores se convierten a NaT)
    ventas["Fecha"] = pd.to_datetime(ventas["Fecha"], errors="coerce")
    calendario["Fecha"] = pd.to_datetime(calendario["Fecha"], errors="coerce")

    # # Convertir columnas numéricas de ventas y rellenar valores inválidos con 0
    # ventas["Cantidad"] = pd.to_numeric(ventas["Cantidad"], errors="coerce").fillna(0)
    # ventas["ValorVenta"] = pd.to_numeric(ventas["ValorVenta"], errors="coerce").fillna(0)

    # Normalizar nombre de columna de negocio para mantener consistencia en toda la app
    if "NombreTienda" in negocios.columns and "NombreNegocio" not in negocios.columns:
        negocios = negocios.rename(columns={"NombreTienda": "NombreNegocio"})

    # Columnas de texto a limpiar por cada tabla
    text_cols_clientes = ["ClienteID", "Nombre", "Ciudad", "Segmento"]
    text_cols_productos = ["ProductoID", "NombreProducto", "Categoria"]
    text_cols_negocios = ["NegocioID", "NombreNegocio", "Ciudad"]

    # Limpiar espacios en blanco en columnas de texto de clientes
    for col in text_cols_clientes:
        if col in clientes.columns:
            clientes[col] = clientes[col].astype(str).str.strip()

    # Limpiar espacios en blanco en columnas de texto de productos
    for col in text_cols_productos:
        if col in productos.columns:
            productos[col] = productos[col].astype(str).str.strip()

    # Limpiar espacios en blanco en columnas de texto de negocios
    for col in text_cols_negocios:
        if col in negocios.columns:
            negocios[col] = negocios[col].astype(str).str.strip()

    # Normalizar columnas ID en ventas para garantizar joins correctos
    for col in ["VentaID", "ClienteID", "ProductoID", "NegocioID"]:
        if col in ventas.columns:
            ventas[col] = ventas[col].astype(str).str.strip()

    return clientes, productos, negocios, calendario, ventas


def load_all_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Carga los 5 archivos CSV y aplica limpieza mínima.
    Retorna: (clientes, productos, negocios, calendario, ventas)
    """
    clientes = load_csv("Clientes.csv")
    productos = load_csv("Productos.csv")
    negocios = load_csv("Negocios.csv")
    calendario = load_csv("Calendario.csv")
    ventas = load_csv("Ventas.csv")

    return clean_dataframes(clientes, productos, negocios, calendario, ventas)


def build_model_dataframe(
    clientes: pd.DataFrame,
    productos: pd.DataFrame,
    negocios: pd.DataFrame,
    calendario: pd.DataFrame,
    ventas: pd.DataFrame,
) -> pd.DataFrame:
    return (
        ventas
        .merge(clientes, on="ClienteID", how="left")
        .merge(productos, on="ProductoID", how="left")
        .merge(negocios, on="NegocioID", how="left", suffixes=("", "_Negocio"))
        .merge(calendario, on="Fecha", how="left")
    )