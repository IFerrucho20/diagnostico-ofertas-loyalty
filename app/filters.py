import pandas as pd
from typing import Optional, List


def apply_filters(
    df: pd.DataFrame,
    fecha_inicio,
    fecha_fin,
    productos_oferta: Optional[List[str]] = None,
    ciudades_cliente: Optional[List[str]] = None,
    segmentos: Optional[List[str]] = None,
    categorias: Optional[List[str]] = None,
    negocios_ids: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Aplica los filtros seleccionados por el usuario al DataFrame base."""
    
    filtered = df.copy()

    filtered = filtered[
        (filtered["Fecha"] >= pd.to_datetime(fecha_inicio)) &
        (filtered["Fecha"] <= pd.to_datetime(fecha_fin))
    ]

    if productos_oferta:
        filtered = filtered[filtered["ProductoID"].isin(productos_oferta)]

    if ciudades_cliente and "Ciudad" in filtered.columns:
        filtered = filtered[filtered["Ciudad"].isin(ciudades_cliente)]

    if segmentos and "Segmento" in filtered.columns:
        filtered = filtered[filtered["Segmento"].isin(segmentos)]

    if categorias and "Categoria" in filtered.columns:
        filtered = filtered[filtered["Categoria"].isin(categorias)]

    if negocios_ids:
        filtered = filtered[filtered["NegocioID"].isin(negocios_ids)]

    return filtered