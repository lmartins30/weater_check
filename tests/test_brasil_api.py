"""
Testes unitários para a integração com a BrasilAPI.
"""

from unittest.mock import Mock, patch

import pytest
from requests.exceptions import Timeout

from src.api.brasil_api import CEPNotFoundError, CEPTimeoutError, fetch_lat_lon


@patch("src.api.brasil_api.requests.get")
def test_fetch_lat_lon_success(mock_get):
    """Testa o caso de sucesso onde o JSON contém lat/lon corretos."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "location": {"coordinates": {"latitude": "-23.5505", "longitude": "-46.6333"}}
    }
    mock_get.return_value = mock_response

    lat, lon = fetch_lat_lon("01001000")
    assert lat == -23.5505
    assert lon == -46.6333
    mock_get.assert_called_once()


@patch("src.api.brasil_api.requests.get")
def test_fetch_lat_lon_not_found(mock_get):
    """Testa o retorno 404 (CEP não encontrado)."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    with pytest.raises(CEPNotFoundError):
        fetch_lat_lon("00000000")
    mock_get.assert_called_once()


@patch("src.api.brasil_api.requests.get")
def test_fetch_lat_lon_timeout_and_retries(mock_get):
    """Testa se o timeout dispara os retries configurados no tenacity e gera CEPTimeoutError."""
    # Simula que todas as chamadas levantarão Timeout
    mock_get.side_effect = Timeout("Timeout simulação")

    with pytest.raises(CEPTimeoutError):
        fetch_lat_lon("01001000")

    # Tenacity deve tentar 3 vezes antes de falhar
    assert mock_get.call_count == 3


@patch("src.api.brasil_api.requests.get")
def test_fetch_lat_lon_invalid_structure(mock_get):
    """Testa o caso de o CEP existir, mas o JSON não ter a estrutura de lat/lon esperada."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"location": {"coordinates": {}}}  # Estrutura errada
    mock_get.return_value = mock_response

    with pytest.raises(ValueError):
        fetch_lat_lon("01001000")
