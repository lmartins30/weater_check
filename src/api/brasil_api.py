"""
Módulo responsável pela integração com a BrasilAPI para geocodificação via CEP.
"""

import logging
from typing import Tuple

import requests
from requests.exceptions import Timeout
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class CEPNotFoundError(Exception):
    """Exceção levantada quando um CEP não é encontrado (HTTP 404)."""


class CEPTimeoutError(Exception):
    """Exceção levantada quando a requisição de CEP sofre timeout persistente."""


class _BrasilAPIServerError(Exception):
    """Exceção interna para disparar retries em erros 5xx."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((Timeout, _BrasilAPIServerError)),
    reraise=True,
)
def _get_lat_lon_from_cep(cep: str) -> Tuple[float, float]:
    """
    Busca latitude e longitude para um determinado CEP usando a BrasilAPI (função interna).
    """
    url = f"https://brasilapi.com.br/api/cep/v2/{cep}"
    logger.info("Consultando BrasilAPI para o CEP: %s", cep)

    try:
        response = requests.get(url, timeout=10)
    except Timeout as exc:
        logger.warning("Timeout ao acessar BrasilAPI para CEP %s", cep)
        raise exc  # Tenacity capturará e tentará novamente

    if response.status_code == 404:
        logger.warning("CEP não encontrado: %s", cep)
        raise CEPNotFoundError(f"CEP {cep} não foi encontrado.")

    if response.status_code >= 500:
        logger.warning("Erro de servidor na BrasilAPI para CEP %s", cep)
        raise _BrasilAPIServerError(f"Erro no servidor da BrasilAPI: {response.status_code}")

    response.raise_for_status()
    data = response.json()

    try:
        lat = float(data["location"]["coordinates"]["latitude"])
        lon = float(data["location"]["coordinates"]["longitude"])
        return lat, lon
    except (KeyError, TypeError, ValueError) as exc:
        logger.error("Falha ao extrair coordenadas do CEP %s. Resposta: %s", cep, data)
        raise ValueError(f"Estrutura inesperada na resposta do CEP {cep}") from exc


def fetch_lat_lon(cep: str) -> Tuple[float, float]:
    """
    Busca latitude e longitude para um determinado CEP, com tolerância a falhas.

    Args:
        cep (str): O CEP a ser buscado (somente números ou formato padrão).

    Returns:
        Tuple[float, float]: Latitude e Longitude (nesta ordem).

    Raises:
        CEPNotFoundError: Se o CEP não existir (HTTP 404).
        CEPTimeoutError: Se houver timeout repetidas vezes (limite de 10s).
        ValueError: Se a estrutura do JSON estiver inválida ou faltarem coordenadas.
    """
    try:
        return _get_lat_lon_from_cep(cep)
    except Timeout as exc:
        raise CEPTimeoutError(f"Timeout após múltiplas tentativas para o CEP {cep}") from exc
    except _BrasilAPIServerError as exc:
        raise Exception(f"Falha persistente no servidor da BrasilAPI: {exc}") from exc
