# -*- coding: utf-8 -*-
"""Untitled0.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1GRRjd3A7tV_ws8e7VxoAqon5NWIyQoX2
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.linear_model import LinearRegression
import numpy as np

st.set_page_config(layout="wide")
st.title("📈 Análisis y Proyección de Compras Globales")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("ecommerce-data.csv", encoding='ISO-8859-1')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    return df

df = load_data()

# Panel lateral (sidebar) con información y filtros
st.sidebar.header("Filtros")

# Mostrar países disponibles
paises_disponibles = sorted(df['Country'].dropna().unique())
st.sidebar.info(f"🌍 Países con datos disponibles: {', '.join(paises_disponibles)}")

# Selector de país
country = st.sidebar.selectbox("Selecciona un país", paises_disponibles)

# Mostrar rango de fechas disponible
min_date = df['InvoiceDate'].min().date()
max_date = df['InvoiceDate'].max().date()
st.sidebar.info(f"📅 Rango de fechas disponible: {min_date} → {max_date}")

# Selector de rango de fechas
date_range = st.sidebar.date_input(
    "Selecciona el rango de fechas",
    [min_date, max_date]
)

# Validar rango de fechas
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    # Filtrar y copiar
    filtered_df = df[
        (df['Country'] == country) &
        (df['InvoiceDate'] >= start_date) &
        (df['InvoiceDate'] <= end_date)
    ].copy()

    if filtered_df.empty:
        st.warning("⚠️ No hay datos para los filtros seleccionados.")
    else:
        # 🏆 Top 10 productos más vendidos
        product_sales = (
            filtered_df.groupby('Description')['Quantity']
            .sum()
            .reset_index()
            .sort_values(by='Quantity', ascending=False)
            .head(10)
        )

        st.subheader(f"🏆 Top 10 productos más vendidos en {country}")
        fig = px.bar(product_sales, x='Quantity', y='Description', orientation='h')
        st.plotly_chart(fig, use_container_width=True)

        # 📈 Tendencia y proyección
        filtered_df['Month'] = filtered_df['InvoiceDate'].dt.to_period('M').dt.to_timestamp()
        ventas_mensuales = (
            filtered_df.groupby('Month')['Quantity']
            .sum()
            .reset_index()
            .rename(columns={'Quantity': 'Ventas'})
        )

        # Crear variable numérica
        ventas_mensuales['Mes_Num'] = np.arange(len(ventas_mensuales))

        X = ventas_mensuales[['Mes_Num']]
        y = ventas_mensuales['Ventas']

        modelo = LinearRegression()
        modelo.fit(X, y)

        # Predicción para próximos 6 meses
        meses_futuros = 6
        futuros_num = np.arange(len(ventas_mensuales), len(ventas_mensuales) + meses_futuros)
        futuros_x = pd.DataFrame({'Mes_Num': futuros_num})
        predicciones = modelo.predict(futuros_x)

        fechas_futuras = pd.date_range(
            start=ventas_mensuales['Month'].max() + pd.offsets.MonthBegin(1),
            periods=meses_futuros,
            freq='MS'
        )

        df_pred = pd.DataFrame({
            'Month': fechas_futuras,
            'Ventas': predicciones,
            'Tipo': 'Proyección'
        })

        df_real = ventas_mensuales[['Month', 'Ventas']].copy()
        df_real['Tipo'] = 'Real'

        df_combinado = pd.concat([df_real, df_pred], ignore_index=True)

        # Mostrar gráfico combinado
        st.subheader(f"📊 Tendencia y proyección de ventas en {country}")
        fig2 = px.line(
            df_combinado,
            x='Month',
            y='Ventas',
            color='Tipo',
            markers=True,
            title=f"Ventas reales y proyección para los próximos {meses_futuros} meses"
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("⚠️ Por favor selecciona un rango de fechas válido.")