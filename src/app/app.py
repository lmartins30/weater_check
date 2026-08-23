"""
Interface principal da aplicação Streamlit.
"""

import datetime
import logging

import pandas as pd
import plotly.express as px
import streamlit as st

from src.api.brasil_api import CEPNotFoundError, CEPTimeoutError, fetch_lat_lon
from src.api.open_meteo import fetch_weather_history
from src.pipeline.cleaning import clean_precipitation, clean_temperature
from src.pipeline.metrics import (
    calculate_precipitation_confusion_matrix,
    calculate_temperature_error,
)

logger = logging.getLogger(__name__)


# Configurar o Streamlit para usar cache nas chamadas de rede
@st.cache_data(ttl=3600)
def get_weather_data(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Busca os dados e converte para DataFrame com cache habilitado."""
    response = fetch_weather_history(lat, lon, start_date, end_date)

    df = pd.DataFrame(
        {
            "time": response.hourly.time,
            "temperature_2m": response.hourly.temperature_2m,
            "precipitation": response.hourly.precipitation,
        }
    )
    df["time"] = pd.to_datetime(df["time"])
    return df


def simulate_predictions(df_real: pd.DataFrame) -> pd.DataFrame:
    """
    Função mock para gerar previsões sintéticas para o Dashboard,
    pois no momento temos apenas a integração da API de histórico real (target).
    """
    df = df_real.copy()
    import numpy as np

    # Adiciona ruído de -3 a +3 na temperatura
    ruido_temp = np.random.uniform(-3, 3, len(df))
    df["temp_prevista"] = df["temperature_2m"] + ruido_temp

    # Adiciona ruído na precipitação (chuva)
    ruido_prec = np.random.uniform(-1, 1, len(df))
    df["prec_prevista"] = (df["precipitation"] + ruido_prec).clip(lower=0.0)

    return df


def main():
    st.set_page_config(page_title="Weather Metrics Dashboard", layout="wide")
    st.title("🌦️ Dashboard de Avaliação de Previsões")

    with st.sidebar:
        st.header("Configurações")
        cep = st.text_input("Digite o CEP (somente números):", "01001000")

        col1, col2 = st.columns(2)
        with col1:
            start_d = st.date_input(
                "Data Inicial", datetime.date.today() - datetime.timedelta(days=7)
            )
        with col2:
            end_d = st.date_input("Data Final", datetime.date.today())

        btn_buscar = st.button("Analisar", use_container_width=True)

    if btn_buscar:
        if len(cep) != 8 or not cep.isdigit():
            st.error("Por favor, digite um CEP válido com 8 números (ex: 01001000).")
            return

        # 1. Geocodificação (BrasilAPI)
        try:
            with st.spinner("Buscando coordenadas (BrasilAPI)..."):
                lat, lon = fetch_lat_lon(cep)
            st.success(f"📍 Coordenadas encontradas: Lat {lat}, Lon {lon}")
        except CEPNotFoundError:
            st.warning("⚠️ O CEP digitado não foi encontrado na base.")
            return
        except CEPTimeoutError:
            st.error("❌ Ocorreu um timeout ao tentar se comunicar com a BrasilAPI.")
            return
        except Exception as e:
            st.error(f"❌ Erro inesperado ao buscar CEP: {e}")
            return

        # 2. Dados Meteorológicos Históricos (Open-Meteo)
        try:
            with st.spinner("Buscando dados históricos (Open-Meteo)..."):
                df_real = get_weather_data(
                    lat, lon, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")
                )
        except Exception as e:
            st.error(f"❌ Erro ao buscar dados na Open-Meteo: {e}")
            return

        # 3. Limpeza dos Dados (Pipeline)
        df_real = clean_temperature(df_real, "temperature_2m")
        df_real = clean_precipitation(df_real, "precipitation")

        if df_real.empty:
            st.warning("⚠️ Não há dados suficientes após a limpeza (buracos muito longos).")
            return

        # Simula as previsões (até conectarmos com o modelo de ML futuramente)
        df = simulate_predictions(df_real)

        # 4. Cálculo de Métricas
        df = calculate_temperature_error(df, col_real="temperature_2m", col_prev="temp_prevista")
        matriz = calculate_precipitation_confusion_matrix(
            df, col_real="precipitation", col_prev="prec_prevista"
        )

        st.markdown("---")
        st.header("📊 Análise de Temperatura")

        total_acertos = df["acerto_temp"].sum()
        total_validos = len(df)
        acuracia = (total_acertos / total_validos) * 100 if total_validos > 0 else 0

        st.metric(label="Acurácia (Erro <= 2°C)", value=f"{acuracia:.1f}%")

        # Gráfico Temporal - Plotly
        fig = px.line(
            df,
            x="time",
            y=["temperature_2m", "temp_prevista"],
            labels={"value": "Temperatura (°C)", "time": "Hora", "variable": "Legenda"},
            title="Série Temporal: Real vs. Previsto",
        )
        # Renomeando as legendas
        newnames = {
            "temperature_2m": "Temperatura Real",
            "temp_prevista": "Temperatura Prevista (Simulada)",
        }
        fig.for_each_trace(lambda t: t.update(name=newnames[t.name]))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.header("🌧️ Matriz de Confusão (Precipitação)")
        st.caption("Considerando chuva para valores > 0.1mm")

        # Exibição bonita para Matriz
        mc_col1, mc_col2, mc_col3, mc_col4 = st.columns(4)
        mc_col1.metric("Verdadeiro Positivo (VP)", matriz["VP"], help="Previu chuva e choveu")
        mc_col2.metric("Falso Positivo (FP)", matriz["FP"], help="Previu chuva e não choveu")
        mc_col3.metric("Falso Negativo (FN)", matriz["FN"], help="Previu sol e choveu")
        mc_col4.metric("Verdadeiro Negativo (VN)", matriz["VN"], help="Previu sol e fez sol")


if __name__ == "__main__":
    main()
