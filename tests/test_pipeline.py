"""
Testes unitários para a pipeline de dados e regras de negócio.
"""

import pandas as pd

from src.pipeline.cleaning import clean_precipitation, clean_temperature
from src.pipeline.metrics import (
    calculate_precipitation_confusion_matrix,
    calculate_temperature_error,
    filter_by_lead_time,
)


def test_clean_precipitation():
    """Garante que NaNs em precipitação virem 0.0"""
    df = pd.DataFrame({"precipitation": [1.2, float("nan"), 3.0, None]})
    df_clean = clean_precipitation(df)
    assert df_clean["precipitation"].tolist() == [1.2, 0.0, 3.0, 0.0]


def test_clean_temperature_gap_logic():
    """Garante que buracos <= 2 são interpolados e > 2 são descartados."""
    df = pd.DataFrame(
        {
            "temperature_2m": [
                20.0,
                float("nan"),  # Buraco de 1h (interpolar)
                22.0,
                float("nan"),  # Buraco de 3h (descartar todos os 3)
                float("nan"),
                float("nan"),
                26.0,
            ]
        }
    )
    df_clean = clean_temperature(df)

    # Os índices 3, 4, 5 devem sumir
    assert len(df_clean) == 4

    # O índice 1 deve virar 21.0
    assert df_clean.loc[1, "temperature_2m"] == 21.0

    # O índice 6 deve continuar
    assert df_clean.loc[6, "temperature_2m"] == 26.0


def test_calculate_temperature_error():
    """Garante que o erro absoluto bate e o acerto é booleano correto."""
    df = pd.DataFrame({"temp_real": [20.0, 25.0, 15.0], "temp_prevista": [19.0, 28.0, 15.5]})
    df_res = calculate_temperature_error(df)

    assert df_res["erro_absoluto"].tolist() == [1.0, 3.0, 0.5]
    assert df_res["acerto_temp"].tolist() == [True, False, True]


def test_calculate_precipitation_confusion_matrix():
    """Garante a matriz de confusão considerando o threshold > 0.1mm."""
    df = pd.DataFrame(
        {
            # Threshold: > 0.1
            "prec_real": [0.0, 0.2, 0.5, 0.0],
            "prec_prevista": [0.0, 0.0, 1.0, 0.5],
        }
    )
    # Linha 0: Real <=0.1 (Falso), Prev <=0.1 (Falso) -> VN
    # Linha 1: Real >0.1 (Verdadeiro), Prev <=0.1 (Falso) -> FN
    # Linha 2: Real >0.1 (Verdadeiro), Prev >0.1 (Verdadeiro) -> VP
    # Linha 3: Real <=0.1 (Falso), Prev >0.1 (Verdadeiro) -> FP

    matrix = calculate_precipitation_confusion_matrix(df)

    assert matrix["VN"] == 1
    assert matrix["FN"] == 1
    assert matrix["VP"] == 1
    assert matrix["FP"] == 1


def test_filter_by_lead_time():
    """Garante que a filtragem por diferença de dias (lead time) funciona."""
    df = pd.DataFrame(
        {
            "target_date": ["2023-10-05", "2023-10-05", "2023-10-05"],
            "forecast_date": ["2023-10-04", "2023-10-02", "2023-10-01"],
        }
    )  # Lead times: 1, 3, 4

    df_lead_3 = filter_by_lead_time(df, "target_date", "forecast_date", 3)
    assert len(df_lead_3) == 1
    assert df_lead_3.iloc[0]["forecast_date"] == "2023-10-02"
