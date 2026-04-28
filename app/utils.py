"""
Helpers visuales.
RESPONSABILIDAD: Formateo para UI, sin lógica de negocio.
"""

import pandas as pd


def format_currency(value: float) -> str:
    """Formatea un número como moneda"""
    return f"${value:,.0f}"


def format_percentage(value: float) -> str:
    """Formatea un número como porcentaje"""
    return f"{value:.1f}%"


def format_date(date_value) -> str:
    """Formatea fecha para mostrar en tablas (YYYY-MM-DD)"""
    if pd.isna(date_value):
        return ""
    return pd.to_datetime(date_value).strftime("%Y-%m-%d")


def format_percent(value: float, decimals: int = 1) -> str:
    """Formatea decimal como porcentaje para UI"""
    return f"{value * 100:.{decimals}f}%"