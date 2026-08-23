"""
Módulo de cálculo de regras de negócio e métricas meteorológicas.
"""

import logging
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def calculate_temperature_error(
    df: pd.DataFrame,
    col_real: str = "temp_real",
    col_prev: str = "temp_prevista",
) -> pd.DataFrame:
    """
    Calcula o erro absoluto e sinaliza se houve acerto (erro <= 2°C).
    """
    df_res = df.copy()
    df_res["erro_absoluto"] = (df_res[col_real] - df_res[col_prev]).abs()
    df_res["acerto_temp"] = df_res["erro_absoluto"] <= 2.0

    acertos = df_res["acerto_temp"].sum()
    logger.info("Erro absoluto calculado. Acertos (<= 2°C): %d", acertos)
    return df_res


def calculate_precipitation_confusion_matrix(
    df: pd.DataFrame,
    col_real: str = "prec_real",
    col_prev: str = "prec_prevista",
    threshold: float = 0.1,
) -> Dict[str, int]:
    """
    Calcula VP, FP, FN, VN para precipitação com base no threshold (> 0.1).
    """
    real_chuva = df[col_real] > threshold
    prev_chuva = df[col_prev] > threshold

    vp = ((prev_chuva) & (real_chuva)).sum()
    fp = ((prev_chuva) & (~real_chuva)).sum()
    fn = ((~prev_chuva) & (real_chuva)).sum()
    vn = ((~prev_chuva) & (~real_chuva)).sum()

    logger.info("Matriz de Confusão calculada: VP=%d, FP=%d, FN=%d, VN=%d", vp, fp, fn, vn)

    return {
        "VP": int(vp),
        "FP": int(fp),
        "FN": int(fn),
        "VN": int(vn),
    }


def filter_by_lead_time(
    df: pd.DataFrame, col_target_date: str, col_forecast_date: str, lead_days: int
) -> pd.DataFrame:
    """
    Filtra as previsões geradas exatamente 'lead_days' antes da data alvo.
    """
    diff = (pd.to_datetime(df[col_target_date]) - pd.to_datetime(df[col_forecast_date])).dt.days
    df_filtered = df[diff == lead_days].copy()

    logger.info(
        "Filtrado para Lead Time = %d dias. Restam %d linhas.", lead_days, len(df_filtered)
    )
    return df_filtered
