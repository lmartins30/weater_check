"""
Interface principal da aplicação Streamlit (V2).
"""

import datetime
import logging

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.api.brasil_api import fetch_lat_lon
from src.api.open_meteo import fetch_weather_history
from src.pipeline.cleaning import clean_precipitation, clean_temperature
from src.pipeline.metrics import (
    calculate_precipitation_confusion_matrix,
    calculate_temperature_error,
)

logger = logging.getLogger(__name__)


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
    Função mock para gerar previsões sintéticas para o Dashboard.
    """
    df = df_real.copy()

    # Adiciona ruído de -3 a +3 na temperatura
    ruido_temp = np.random.uniform(-3, 3, len(df))
    df["temp_prevista"] = df["temperature_2m"] + ruido_temp

    # Adiciona ruído na precipitação (chuva)
    ruido_prec = np.random.uniform(-1, 1, len(df))
    df["prec_prevista"] = (df["precipitation"] + ruido_prec).clip(lower=0.0)

    return df


def draw_confidence_horizon():
    """Desenha a simulação de decaimento de acurácia por Lead Time."""
    st.markdown("---")
    st.header("⏳ Horizonte de Confiança (Lead Time)")
    st.markdown("Até qual dia no futuro eu posso confiar na previsão? Veja a curva de decaimento:")

    # Simulação pedagógica de decaimento (não há API gratuita com este histórico)
    days = list(range(1, 8))
    accuracies = [95, 88, 80, 72, 60, 50, 40]

    threshold = 70
    confiable_days = sum(1 for acc in accuracies if acc >= threshold)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=days,
            y=accuracies,
            mode="lines+markers",
            name="Acurácia",
            line=dict(color="royalblue", width=4),
            marker=dict(size=10),
        )
    )
    fig.add_hline(
        y=threshold,
        line_dash="dash",
        line_color="red",
        annotation_text="Limiar de Confiança (70%)",
        annotation_position="bottom right",
    )
    fig.update_layout(
        xaxis_title="Dias de Antecedência",
        yaxis_title="Confiança (%)",
        yaxis_range=[0, 100],
        margin=dict(l=0, r=0, t=30, b=0),
    )

    col_text, col_chart = st.columns([1, 2])
    with col_text:
        st.success(f"### 🛡️ Previsão Segura:\n### {confiable_days} Dias")
        st.write(
            f"Você pode confiar no aplicativo com segurança para os próximos **{confiable_days} dias**."
        )
        st.write(
            f"A partir do **dia {confiable_days + 1}**, a chance de erro fica muito alta. "
            f"Evite planejar eventos críticos ao ar livre baseados nessa distância."
        )
    with col_chart:
        st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(
        page_title="Inteligência Meteorológica", layout="wide", initial_sidebar_state="expanded"
    )
    st.title("🌦️ Dashboard de Inteligência Meteorológica")
    st.markdown("Avalie a qualidade das previsões e descubra até quando confiar no modelo.")

    with st.sidebar:
        st.header("Configurações")
        cep = st.text_input("CEP alvo (ex: 01001000):", "01001000")

        with st.expander("Período de Análise", expanded=True):
            start_d = st.date_input(
                "Data Inicial", datetime.date.today() - datetime.timedelta(days=7)
            )
            end_d = st.date_input("Data Final", datetime.date.today())

        btn_buscar = st.button("Analisar Confiabilidade", use_container_width=True, type="primary")

    if btn_buscar:
        if len(cep) != 8 or not cep.isdigit():
            st.error("Por favor, digite um CEP válido com 8 números (ex: 01001000).")
            return

        try:
            with st.spinner("Buscando localização (BrasilAPI)..."):
                lat, lon = fetch_lat_lon(cep)
        except Exception:
            st.warning("⚠️ O CEP digitado não foi encontrado ou houve erro de conexão.")
            return

        try:
            with st.spinner("Buscando dados históricos (Open-Meteo)..."):
                df_real = get_weather_data(
                    lat, lon, start_d.strftime("%Y-%m-%d"), end_d.strftime("%Y-%m-%d")
                )
        except Exception as e:
            st.error(f"❌ Erro ao buscar dados na Open-Meteo: {e}")
            return

        df_real = clean_temperature(df_real, "temperature_2m")
        df_real = clean_precipitation(df_real, "precipitation")
        if df_real.empty:
            st.warning("⚠️ Não há dados suficientes após a limpeza.")
            return

        # Simulação
        df = simulate_predictions(df_real)
        df = calculate_temperature_error(df, col_real="temperature_2m", col_prev="temp_prevista")
        matriz = calculate_precipitation_confusion_matrix(
            df, col_real="precipitation", col_prev="prec_prevista"
        )

        # 1. HORIZONTE DE CONFIANÇA (LEAD TIME)
        draw_confidence_horizon()

        # 2. ANÁLISE DE TEMPERATURA
        st.markdown("---")
        st.header("🌡️ Análise de Temperatura")
        st.info(
            "💡 **Como lemos isso?** Consideramos um **'Acerto'** se a previsão errou a temperatura "
            "do momento em no máximo 2°C (para cima ou para baixo)."
        )

        total_acertos = df["acerto_temp"].sum()
        total_validos = len(df)
        acuracia = (total_acertos / total_validos) * 100 if total_validos > 0 else 0

        pior_erro = df["erro_absoluto"].max()
        hora_pior_erro = df.loc[df["erro_absoluto"].idxmax(), "time"].strftime("%d/%m %H:%M")

        tcol1, tcol2 = st.columns(2)
        tcol1.metric(label="Acurácia Geral da Temperatura", value=f"{acuracia:.1f}%")
        tcol2.metric(
            label="Maior Erro Registrado",
            value=f"{pior_erro:.1f}°C",
            delta=f"Ocorreu em {hora_pior_erro}",
            delta_color="inverse",
        )

        fig_temp = px.line(
            df,
            x="time",
            y=["temperature_2m", "temp_prevista"],
            labels={"value": "Temperatura (°C)", "time": "Data e Hora"},
            title="Curva de Temperatura Diária",
        )
        fig_temp.for_each_trace(
            lambda t: t.update(
                name="Real" if t.name == "temperature_2m" else "Previsto (Simulado)"
            )
        )
        st.plotly_chart(fig_temp, use_container_width=True)

        # 3. ANÁLISE DE PRECIPITAÇÃO (Sem jargões)
        st.markdown("---")
        st.header("🌧️ Confiabilidade da Chuva")
        st.caption("Classificação dos dias baseada na comparação de chuva prevista vs realizada.")

        total_chuva = sum(matriz.values())
        conf_chuva = ((matriz["VP"] + matriz["VN"]) / total_chuva) * 100 if total_chuva > 0 else 0
        st.metric(
            "Índice Geral de Acerto (Choveu quando disse que ia chover?)", f"{conf_chuva:.1f}%"
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.success(f"### ✅ {matriz['VP']}\n**Acertou a Chuva**\nPreviu chuva e choveu")
        m2.success(f"### ☀️ {matriz['VN']}\n**Acertou o Sol**\nPreviu sol e fez sol")
        m3.warning(f"### ❌ {matriz['FP']}\n**Alarme Falso**\nPreviu chuva, mas fez sol")
        m4.error(f"### ☔ {matriz['FN']}\n**Chuva Surpresa**\nPreviu sol, mas choveu!")


if __name__ == "__main__":
    main()
