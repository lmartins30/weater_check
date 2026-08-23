"""
Módulo responsável pela integração com a Open-Meteo API.
"""

import logging
from typing import List, Optional

import requests
from pydantic import BaseModel, field_validator

logger = logging.getLogger(__name__)


class OpenMeteoHourly(BaseModel):
    """Schema para validação do bloco hourly da Open-Meteo."""

    time: List[str]
    temperature_2m: List[Optional[float]]
    precipitation: List[Optional[float]]


class OpenMeteoResponse(BaseModel):
    """Schema principal de validação do retorno da Open-Meteo."""

    hourly: OpenMeteoHourly

    @field_validator("hourly")
    @classmethod
    def validate_arrays_length(cls, hourly: OpenMeteoHourly) -> OpenMeteoHourly:
        """Garante que todas as variáveis meteorológicas tenham a mesma janela de tempo."""
        time_len = len(hourly.time)
        if len(hourly.temperature_2m) != time_len:
            raise ValueError("O tamanho de 'temperature_2m' difere do tamanho de 'time'.")
        if len(hourly.precipitation) != time_len:
            raise ValueError("O tamanho de 'precipitation' difere do tamanho de 'time'.")
        return hourly


def fetch_weather_history(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    timezone: str = "America/Sao_Paulo",
) -> OpenMeteoResponse:
    """
    Busca dados históricos e previsões meteorológicas na Open-Meteo.

    Args:
        latitude (float): Latitude do local.
        longitude (float): Longitude do local.
        start_date (str): Data inicial no formato YYYY-MM-DD.
        end_date (str): Data final no formato YYYY-MM-DD.
        timezone (str): Fuso horário obrigatório. Padrão: America/Sao_Paulo.

    Returns:
        OpenMeteoResponse: Objeto Pydantic contendo os dados validados.

    Raises:
        ValueError: Se a resposta da API for inválida ou o contrato quebrar.
        requests.HTTPError: Se houver falha na rede (ex: 4xx, 5xx).
    """
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "temperature_2m,precipitation",
        "timezone": timezone,
    }
    logger.info("Buscando dados na Open-Meteo para %s, %s", latitude, longitude)

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    # Validação rigorosa com Pydantic
    data = response.json()
    try:
        return OpenMeteoResponse(**data)
    except Exception as exc:
        logger.error("Falha de validação do contrato da Open-Meteo: %s", exc)
        raise ValueError(f"Contrato da Open-Meteo violado: {exc}") from exc
