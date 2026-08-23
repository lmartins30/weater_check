"""
Módulo responsável pela limpeza e tratamento de dados climáticos.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


def clean_precipitation(df: pd.DataFrame, col_name: str = "precipitation") -> pd.DataFrame:
    """
    Preenche valores nulos de precipitação com 0.0 (assumindo ausência de chuva).
    """
    df_clean = df.copy()
    df_clean[col_name] = df_clean[col_name].fillna(0.0)
    logger.info("Valores nulos de %s preenchidos com 0.0", col_name)
    return df_clean


def clean_temperature(df: pd.DataFrame, col_name: str = "temperature_2m") -> pd.DataFrame:
    """
    Trata valores nulos de temperatura conforme regras de negócio:
    - Lacunas de até 2 horas consecutivas: Aplicar interpolação linear.
    - Lacunas maiores que 2 horas: Descartar a linha inteira para evitar que
      dados altamente sintéticos interfiram na acurácia do erro.
    """
    df_clean = df.copy()

    # Identificar blocos de NaNs
    is_na = df_clean[col_name].isna()
    groups = (is_na != is_na.shift()).cumsum()

    # Calcular o tamanho de cada bloco de NaNs
    na_sizes = df_clean.groupby(groups)[col_name].transform(
        lambda x: len(x) if x.isna().all() else 0
    )

    # Interpolar linearmente tudo
    df_clean[col_name] = df_clean[col_name].interpolate(method="linear")

    # Sobrescrever de volta com NaN onde o buraco era maior que 2
    df_clean.loc[na_sizes > 2, col_name] = float("nan")

    # Descartar as linhas com NaN resultantes
    initial_len = len(df_clean)
    df_clean = df_clean.dropna(subset=[col_name])
    dropped_rows = initial_len - len(df_clean)

    logger.info(
        "Limpeza de %s concluída: interpolados buracos <= 2h, "
        "removidas %d linhas de grandes lacunas.",
        col_name,
        dropped_rows,
    )

    return df_clean
