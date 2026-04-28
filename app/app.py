"""
Aplicación principal Streamlit.
RESPONSABILIDAD: UI, captura de filtros, llamado a módulos.
NO debe contener lógica de negocio ni merges.
"""

import pandas as pd
import streamlit as st
from io import BytesIO
from load_data import load_all_data, build_model_dataframe
from filters import apply_filters
from metrics import (
    get_qualified_customers,
    calculate_main_kpis,
    calculate_previous_period_sales,
    calculate_variation,
    get_previous_period_customers_over_threshold,
    build_customer_summary,
    build_transaction_detail,
    build_pareto_products,
)

from utils import format_currency, format_percentage, format_date


st.set_page_config(page_title="Diagnóstico de Ofertas Loyalty", layout="wide")

st.title("📊 Diagnóstico de Ofertas - Loyalty")
st.caption("Aplicativo para segmentación dinámica, métricas y exportación de resultados.")


@st.cache_data
def get_model():
    clientes, productos, negocios, calendario, ventas = load_all_data()
    return build_model_dataframe(clientes, productos, negocios, calendario, ventas), productos, negocios


df, productos, negocios = get_model()

if df.empty:
    st.error("No hay datos disponibles para analizar.")
    st.stop()

fecha_min = df["Fecha"].min().date()
fecha_max = df["Fecha"].max().date()

st.sidebar.header("🎛️ Filtros")

rango_oferta = st.sidebar.date_input(
    "Periodo de oferta",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)




if len(rango_oferta) != 2:
    st.warning("Selecciona fecha inicial y fecha final para el periodo de oferta.")
    st.stop()

# Opciones amigables para productos: ID + nombre
productos_opciones = (
    df[["ProductoID", "NombreProducto"]]
    .drop_duplicates()
    .dropna()
    .sort_values(by="ProductoID")
)

mapa_productos = {
    f"{row['ProductoID']} - {row['NombreProducto']}": row["ProductoID"]
    for _, row in productos_opciones.iterrows()
}

productos_labels = st.sidebar.multiselect(
    "Productos de la oferta",
    options=list(mapa_productos.keys()),
    default=list(mapa_productos.keys())[:3],
)

productos_oferta = [mapa_productos[label] for label in productos_labels]

monto_min_oferta = st.sidebar.number_input(
    "Monto mínimo en la oferta",
    min_value=0.0,
    value=55000.0,
    step=5000.0,
)


# Después de definir fecha_min y fecha_max
st.sidebar.subheader("📆 Periodo comparativo")

# Valor por defecto seguro: el mismo rango que la oferta
default_comparativo = (fecha_min, fecha_max)

rango_comparativo = st.sidebar.date_input(
    "Periodo comparativo",
    value=default_comparativo,
    min_value=fecha_min,
    max_value=fecha_max,
)

if len(rango_comparativo) != 2:
    st.warning("Selecciona fecha inicial y fecha final para el periodo comparativo.")
    st.stop()

monto_min_comparativo = st.sidebar.number_input(
    "Monto mínimo periodo comparativo",
    min_value=0.0,
    value=30000.0,
    step=5000.0,
)

ciudades_cliente = st.sidebar.multiselect(
    "Ciudad del cliente",
    options=sorted(df["Ciudad"].dropna().unique().tolist()),
)

segmentos = st.sidebar.multiselect(
    "Segmento",
    options=sorted(df["Segmento"].dropna().unique().tolist()),
)

categorias = st.sidebar.multiselect(
    "Categoría",
    options=sorted(df["Categoria"].dropna().unique().tolist()),
)

# Opciones amigables para negocio: ID + nombre negocio
negocios_opciones = (
    df[["NegocioID", "NombreNegocio"]]
    .drop_duplicates()
    .dropna()
    .sort_values(by="NegocioID")
)

mapa_negocios = {
    f"{row['NegocioID']} - {row['NombreNegocio']}": row["NegocioID"]
    for _, row in negocios_opciones.iterrows()
}

negocios_labels = st.sidebar.multiselect(
    "Negocio",
    options=list(mapa_negocios.keys()),
)

negocios_ids = [mapa_negocios[label] for label in negocios_labels]

columnas_resumen = st.sidebar.multiselect(
    "Columnas para tabla resumen",
    options=[
        "ClienteID", "Nombre", "Ciudad", "Segmento",
        "Total_Gastado_Oferta", "Transacciones_Oferta", "Unidades_Oferta"
    ],
    default=[
        "ClienteID", "Nombre", "Ciudad", "Segmento",
        "Total_Gastado_Oferta", "Transacciones_Oferta"
    ],
)

# Aplicar filtros al periodo de oferta
df_offer = apply_filters(
    df=df,
    fecha_inicio=rango_oferta[0],
    fecha_fin=rango_oferta[1],
    productos_oferta=productos_oferta,
    ciudades_cliente=ciudades_cliente,
    segmentos=segmentos,
    categorias=categorias,
    negocios_ids=negocios_ids,
)

# Obtener clientes calificados (cumplen monto mínimo por transacción)
tx_offer, df_clientes_ok = get_qualified_customers(df_offer, monto_min_oferta)

# Aplicar filtros al periodo comparativo
df_previous_offer = apply_filters(
    df=df,
    fecha_inicio=rango_comparativo[0],
    fecha_fin=rango_comparativo[1],
    productos_oferta=productos_oferta,
    ciudades_cliente=ciudades_cliente,
    segmentos=segmentos,
    categorias=categorias,
    negocios_ids=negocios_ids,
)

# Clientes que cumplieron en periodo anterior
previous_customers = get_previous_period_customers_over_threshold(
    df_previous_offer,
    monto_min_comparativo,
)

clientes_prev_ok = previous_customers.loc[
    previous_customers["CumplePeriodoAnterior"],
    "ClienteID"
].unique()

# Clientes que cumplieron en AMBOS periodos
df_clientes_actual_y_prev = df_clientes_ok[
    df_clientes_ok["ClienteID"].isin(clientes_prev_ok)
].copy()

# Calcular KPIs
kpis_actual = calculate_main_kpis(df_clientes_ok)
venta_actual = kpis_actual["venta_total"]
venta_anterior = calculate_previous_period_sales(df_previous_offer)
variacion = calculate_variation(venta_actual, venta_anterior)

# Mostrar KPIs
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("👥 Clientes únicos", kpis_actual["clientes_unicos"])
col2.metric("🛒 Transacciones", kpis_actual["transacciones"])
col3.metric("💰 Venta oferta", format_currency(venta_actual))
col4.metric("📦 Unidades vendidas", int(kpis_actual["unidades"]))
col5.metric("📊 Variación", format_percentage(variacion), delta=format_percentage(variacion))

st.subheader("🏆 Clientes que además cumplieron en el periodo comparativo")
st.write(
    f"Clientes actuales que también compraron mínimo {format_currency(monto_min_comparativo)} "
    f"en el periodo comparativo: **{df_clientes_actual_y_prev['ClienteID'].nunique()}**"
)

# ========== PARETO (UNA SOLA VEZ) ==========
st.subheader("📈 Pareto de productos (80/20)")
st.caption("✅ Los productos marcados con 'Sí' en la columna 'Top 80%' representan el 80% de las ventas totales de la oferta")
pareto = build_pareto_products(df_clientes_ok)
st.dataframe(pareto, use_container_width=True)

# ========== RESUMEN CLIENTES ==========
st.subheader("📋 Resumen de clientes segmentados")
summary = build_customer_summary(df_clientes_ok)

if columnas_resumen:
    columnas_validas = [col for col in columnas_resumen if col in summary.columns]
    st.dataframe(summary[columnas_validas], use_container_width=True)
else:
    st.dataframe(summary, use_container_width=True)

# ========== DETALLE TRANSACCIONAL ==========
st.subheader("📝 Detalle transaccional")
detail = build_transaction_detail(df_clientes_ok)
if not detail.empty and "Fecha" in detail.columns:
    detail["Fecha"] = detail["Fecha"].apply(format_date)
st.dataframe(detail, use_container_width=True)


# ========== EXPORTAR TABLA INDIVIDUAL ==========
st.markdown("---")
st.subheader("📥 Descarga de archivos")
st.caption("Selecciona la tabla que quieres exportar y descarga únicamente esa hoja en Excel.")

# Función para exportar un solo DataFrame a Excel
def export_single_df(df: pd.DataFrame, sheet_name: str) -> bytes:
    # Excel no permite: : \ / ? * [ ]
    safe_sheet_name = (
        sheet_name
        .replace(":", "")
        .replace("\\", "")
        .replace("/", "-")
        .replace("?", "")
        .replace("*", "")
        .replace("[", "")
        .replace("]", "")
    )[:31]

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
        worksheet = writer.sheets[safe_sheet_name]

        for idx, col in enumerate(df.columns):
            max_len = max(
                len(str(col)),
                df[col].astype(str).map(len).max() if not df.empty else 10
            )
            worksheet.set_column(idx, idx, min(max_len + 2, 35))

    output.seek(0)
    return output.getvalue()

# Tablas disponibles para exportar
hojas_disponibles = {
    "Resumen de clientes": summary,
    "Detalle transaccional": detail,
    "Pareto 80/20": pareto,
    "Clientes periodo comparativo": previous_customers,
    "Transacciones de la oferta": tx_offer,
}

# Solo mostrar tablas con información
hojas_validas = {nombre: df for nombre, df in hojas_disponibles.items() if not df.empty}

if hojas_validas:
    hoja_seleccionada = st.selectbox(
        "Selecciona la tabla que quieres exportar:",
        list(hojas_validas.keys())
    )

    df_seleccionado = hojas_validas[hoja_seleccionada]
    nombre_archivo = hoja_seleccionada.lower().replace(" ", "_").replace("/", "-") + ".xlsx"

    st.download_button(
        label=f"📄 Exportar '{hoja_seleccionada}' a Excel",
        data=export_single_df(df_seleccionado, hoja_seleccionada),
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("No hay tablas con datos para exportar con los filtros actuales.")

# ========== EXPLICACIÓN DE MÉTRICAS (en lugar de gráficos feos) ==========
st.subheader("📊 Interpretación de resultados")

with st.expander("ℹ️ ¿Qué significan estos números?", expanded=True):
    st.markdown("""
    | Métrica | Qué significa | Por qué es importante |
    |---------|---------------|----------------------|
    | **Clientes únicos** | Número de clientes que compraron productos de la oferta y cumplieron el monto mínimo por transacción | Mide el alcance de la oferta |
    | **Transacciones** | Total de compras que cumplen la condición | Indica frecuencia de compra |
    | **Venta oferta** | Monto total vendido en productos de la oferta | Impacto económico directo |
    | **Unidades vendidas** | Cantidad total de productos vendidos | Volumen de movimiento |
    | **Variación** | Cambio porcentual vs periodo anterior | Tendencia de la oferta |
    | **Top 80% (Pareto)** | Productos que generan el 80% de las ventas | Dónde enfocar esfuerzos |
    """)

