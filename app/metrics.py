import pandas as pd


def get_transactions_over_threshold(
    df_offer: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """Calcula transacciones que cumplen el monto mínimo de la oferta."""
    tx = (
        df_offer
        .groupby(["ClienteID", "VentaID"], as_index=False)
        .agg(
            ValorOfertaTx=("ValorVenta", "sum"),
            UnidadesTx=("Cantidad", "sum")
        )
    )

    tx["CumpleMontoOferta"] = tx["ValorOfertaTx"] >= threshold
    return tx


def get_qualified_customers(
    df_offer: pd.DataFrame,
    threshold: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Retorna transacciones evaluadas y clientes que cumplen el umbral."""
    tx = get_transactions_over_threshold(df_offer, threshold)
    clientes_ok = tx.loc[tx["CumpleMontoOferta"], "ClienteID"].unique()
    df_clientes_ok = df_offer[df_offer["ClienteID"].isin(clientes_ok)].copy()
    return tx, df_clientes_ok


def calculate_main_kpis(df: pd.DataFrame) -> dict:
    """Calcula KPIs principales."""
    return {
        "clientes_unicos": int(df["ClienteID"].nunique()) if not df.empty else 0,
        "transacciones": int(df["VentaID"].nunique()) if not df.empty else 0,
        "venta_total": float(df["ValorVenta"].sum()) if not df.empty else 0.0,
        "unidades": float(df["Cantidad"].sum()) if not df.empty else 0.0,
    }


def calculate_previous_period_sales(df_previous: pd.DataFrame) -> float:
    """Calcula la venta total del periodo comparativo."""
    return 0.0 if df_previous.empty else float(df_previous["ValorVenta"].sum())


def calculate_variation(current_sales: float, previous_sales: float) -> float:
    """Calcula la variación porcentual entre dos periodos."""
    if previous_sales == 0:
        return 0.0
    return ((current_sales - previous_sales) / previous_sales) * 100


def get_previous_period_customers_over_threshold(
    df_previous_offer: pd.DataFrame,
    threshold_previous: float,
) -> pd.DataFrame:
    """Calcula clientes que cumplen el umbral en el periodo comparativo."""
    prev_customer_sales = (
        df_previous_offer
        .groupby("ClienteID", as_index=False)
        .agg(VentaAnteriorOferta=("ValorVenta", "sum"))
    )

    prev_customer_sales["CumplePeriodoAnterior"] = (
        prev_customer_sales["VentaAnteriorOferta"] >= threshold_previous
    )

    return prev_customer_sales


def build_customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Construye resumen por cliente."""
    if df.empty:
        return pd.DataFrame(columns=[
            "ClienteID", "Nombre", "Ciudad", "Segmento",
            "Total_Gastado_Oferta", "Transacciones_Oferta", "Unidades_Oferta"
        ])

    return (
        df.groupby(["ClienteID", "Nombre", "Ciudad", "Segmento"], as_index=False)
        .agg(
            Total_Gastado_Oferta=("ValorVenta", "sum"),
            Transacciones_Oferta=("VentaID", "nunique"),
            Unidades_Oferta=("Cantidad", "sum"),
        )
        .sort_values(by="Total_Gastado_Oferta", ascending=False)
    )


def build_transaction_detail(df: pd.DataFrame) -> pd.DataFrame:
    """Construye detalle transaccional."""
    columns = [
        "VentaID", "Fecha", "ClienteID", "Nombre", "Ciudad", "Segmento",
        "ProductoID", "NombreProducto", "Categoria", "NegocioID", "NombreNegocio",
        "Cantidad", "ValorVenta"
    ]
    available_cols = [col for col in columns if col in df.columns]
    return df[available_cols].sort_values(by=["Fecha", "VentaID"]).copy()


def build_pareto_products(df: pd.DataFrame) -> pd.DataFrame:
    """Construye tabla Pareto 80/20."""
    if df.empty:
        return pd.DataFrame(columns=["Producto", "Venta", "% Venta", "% Acumulado", "Top 80%"])

    pareto = (
        df.groupby("NombreProducto", as_index=False)
        .agg(Venta=("ValorVenta", "sum"))
        .sort_values(by="Venta", ascending=False)
        .reset_index(drop=True)
        .rename(columns={"NombreProducto": "Producto"})
    )

    total = pareto["Venta"].sum()
    if total == 0:
        return pd.DataFrame(columns=["Producto", "Venta", "% Venta", "% Acumulado", "Top 80%"])

    pareto["% Venta"] = (pareto["Venta"] / total * 100).round(1).astype(str) + "%"
    pareto["% Acumulado"] = (pareto["Venta"] / total * 100).cumsum().round(1).astype(str) + "%"

    acumulado = pareto["Venta"].cumsum()
    idx_top80 = (acumulado >= total * 0.8).idxmax()
    pareto["Top 80%"] = ""
    pareto.loc[:idx_top80, "Top 80%"] = "✅ Sí"

    return pareto[["Producto", "Venta", "% Venta", "% Acumulado", "Top 80%"]]


