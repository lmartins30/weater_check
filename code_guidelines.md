# Python Code Guidelines & Best Practices

Este documento estabelece as diretrizes e boas práticas para o desenvolvimento de código Python, garantindo legibilidade, manutenibilidade e consistência em nossos projetos.

## 1. Estilo de Código (PEP 8)

Seguimos as diretrizes oficiais do [PEP 8](https://peps.python.org/pep-0008/). Abaixo estão os pontos mais importantes:

### Nomenclatura
* **Variáveis e Funções:** `snake_case` (letras minúsculas com palavras separadas por sublinhado).
* **Classes e Exceções:** `PascalCase` / `CamelCase` (palavras iniciadas com letras maiúsculas, sem separadores).
* **Constantes:** `UPPER_SNAKE_CASE` (letras maiúsculas separadas por sublinhado).
* **Módulos e Pacotes:** Nomes curtos e em minúsculas (preferencialmente sem sublinhados).

### Formatação
* **Indentação:** 4 espaços por nível de indentação (nunca use *tabs*).
* **Tamanho máximo da linha:** 79 caracteres para código, 72 para docstrings e comentários (limite flexível até 99 caracteres se melhorar muito a legibilidade).
* **Linhas em branco:** 
  * Duas linhas em branco antes de classes e funções no nível principal (top-level).
  * Uma linha em branco antes de métodos dentro de uma classe.
* **Imports:** Devem ficar sempre no topo do arquivo, ordenados da seguinte forma:
  1. Imports da biblioteca padrão (ex: `os`, `sys`).
  2. Imports de bibliotecas de terceiros (ex: `pandas`, `requests`).
  3. Imports locais da própria aplicação.

---

## 2. Docstrings (Padrão Google)

A documentação do código é obrigatória para funções públicas, classes e módulos. Utilizamos o formato **Google Docstring**.

### Exemplo de Função:
```python
def fetch_data(url: str, timeout: int = 10) -> dict:
    """
    Busca dados de uma API externa.

    Args:
        url (str): A URL do endpoint da API.
        timeout (int, optional): Tempo limite da requisição em segundos. Padrão é 10.

    Returns:
        dict: Um dicionário contendo a resposta em JSON.

    Raises:
        ConnectionError: Se a conexão com a API falhar.
        ValueError: Se a URL fornecida for inválida.
    """
    pass
```

---

## 3. Tipagem (Type Hinting)

Sempre utilize *Type Hints* (PEP 484) nas assinaturas de funções e métodos. Isso facilita a leitura e permite análises estáticas (com ferramentas como `mypy`).

```python
from typing import List, Optional

def process_items(items: List[str], max_retries: Optional[int] = None) -> bool:
    # Implementação
    return True
```

---

## 4. Logging (Registro de Eventos)

**Nunca utilize `print()` em código de produção.** Use a biblioteca padrão `logging`.

* Configure um formato padrão de log com timestamp, nível e mensagem.
* Utilize o nível apropriado:
  * `DEBUG`: Informações detalhadas para diagnóstico.
  * `INFO`: Confirmação de que as coisas estão funcionando como esperado.
  * `WARNING`: Indicação de que algo inesperado aconteceu, mas o software continua funcionando.
  * `ERROR`: Devido a um problema mais grave, o software não conseguiu executar uma função.
  * `CRITICAL`: Erro gravíssimo indicando que o programa pode não conseguir continuar rodando.

### Exemplo:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def connect_database():
    logger.info("Tentando conectar ao banco de dados...")
    try:
        # Lógica de conexão
        logger.info("Conexão bem-sucedida.")
    except Exception as e:
        logger.error(f"Falha na conexão: {e}", exc_info=True)
```

---

## 5. Tratamento de Exceções

* Seja específico: capture exceções exatas (`ValueError`, `KeyError`) em vez de capturar uma exceção genérica (`Exception`), a menos que seja para um log global no nível superior da aplicação.
* Evite blocos `try/except` vazios (`pass`). Pelo menos registre o erro via `logger.warning()` ou `logger.error()`.

---

## 6. Gerenciamento de Dependências e Ambiente

* Nunca instale dependências globalmente. Use ambientes virtuais (`venv`, `pipenv`, `poetry`).
* Sempre mantenha um arquivo de controle de dependências atualizado (`requirements.txt`, `Pipfile` ou `pyproject.toml`).
* Fixe as versões das dependências para produção (ex: `requests==2.28.1`) para evitar quebra por atualizações inesperadas.

---

## 7. Qualidade de Código e Testes

* **Linters/Formatadores:** Recomendado o uso de `black` para formatação automática, `flake8` ou `ruff` para linting (verificação de estilo), e `isort` para ordenação de imports.
* **Testes:** Todo novo código deve ser acompanhado de testes unitários. Utilizamos `pytest`.
