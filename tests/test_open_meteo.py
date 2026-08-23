"""
Testes unitários para a integração com a Open-Meteo.
"""

from unittest.mock import Mock, patch

import pytest

from src.api.open_meteo import OpenMeteoResponse, fetch_weather_history


@patch("src.api.open_meteo.requests.get")
def test_fetch_weather_history_success(mock_get):
    """Testa sucesso garantindo validação de contrato e envio do timezone."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
            "temperature_2m": [22.5, 21.0],
            "precipitation": [0.0, 1.2],
        }
    }
    mock_get.return_value = mock_response

    result = fetch_weather_history(-23.5, -46.6, "2023-01-01", "2023-01-01")
    assert isinstance(result, OpenMeteoResponse)
    assert len(result.hourly.time) == 2
    assert result.hourly.temperature_2m[0] == 22.5

    # Verifica se os argumentos da requisição estão corretos
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert "timezone" in kwargs["params"]
    assert kwargs["params"]["timezone"] == "America/Sao_Paulo"


@patch("src.api.open_meteo.requests.get")
def test_fetch_weather_history_validation_error(mock_get):
    """Testa erro ValueError quando os arrays de retorno têm tamanhos diferentes."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
            "temperature_2m": [22.5],  # Falta 1 elemento (tamanho divergente)
            "precipitation": [0.0, 1.2],
        }
    }
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Contrato da Open-Meteo violado"):
        fetch_weather_history(-23.5, -46.6, "2023-01-01", "2023-01-01")


@patch("src.api.open_meteo.requests.get")
def test_fetch_weather_history_missing_field(mock_get):
    """Testa ausência de um campo obrigatório no JSON (ex: precipitation ausente)."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2023-01-01T00:00"],
            "temperature_2m": [22.5],
            # Sem precipitation
        }
    }
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Contrato da Open-Meteo violado"):
        fetch_weather_history(-23.5, -46.6, "2023-01-01", "2023-01-01")


@patch("src.api.open_meteo.requests.get")
def test_fetch_weather_history_accepts_null(mock_get):
    """Testa se a API tolera valores None (NaN) dentro do schema."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "hourly": {
            "time": ["2023-01-01T00:00", "2023-01-01T01:00"],
            "temperature_2m": [22.5, None],
            "precipitation": [0.0, None],
        }
    }
    mock_get.return_value = mock_response

    result = fetch_weather_history(-23.5, -46.6, "2023-01-01", "2023-01-01")
    assert result.hourly.temperature_2m[1] is None
