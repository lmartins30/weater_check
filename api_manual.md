# Manual de Integração de APIs

## 1. Geocodificação (BrasilAPI)
- **Endpoint:** `GET https://brasilapi.com.br/api/cep/v2/{cep}`
- **Resiliência (Retry Pattern):** Implementar *Exponential Backoff* (ex: via biblioteca `tenacity`). Máximo de 3 tentativas exclusivas para erros `5xx` ou timeouts.
- **Tratamento de Exceções (Matriz de Erros):**
  - `200 OK`: Validar estritamente se o JSON contém as chaves aninhadas `location.coordinates.longitude` e `latitude`.
  - `404 Not Found`: Disparar exceção customizada `CEPNotFoundError`. A interface deve capturar e exibir "CEP não encontrado", sem quebrar o app.
  - `Timeout` (limite de 10s): Disparar exceção customizada `CEPTimeoutError`.

## 2. Dados Meteorológicos (Open-Meteo)
- **Endpoint Base:** `GET https://archive-api.open-meteo.com/v1/archive`
- **Timezone (Crítico):** O parâmetro `timezone` (ex: `America%2FSao_Paulo`) é **obrigatório**. A requisição deve ser feita no fuso local para evitar desalinhamento de janelas móveis durante o cruzamento do clima real vs. previsto.

### 2.1. Contrato de Resposta (Pydantic Schema)
O parser da requisição deve validar o JSON de retorno garantindo a presença e o tipo dos seguintes arrays no nó `hourly`:
- `time`: Lista de strings (formato ISO-8601).
- `temperature_2m`: Lista de `float` (deve tolerar `None`/`NaN`).
- `precipitation`: Lista de `float` (deve tolerar `None`/`NaN`).
- O tamanho (`len()`) da lista de `time` deve ser idêntico ao das variáveis climáticas.

### 2.2. Otimização e Limites (Rate Limiting)
- A API gratuita possui limite de requisições. 
- **Obrigatório:** Implementar cache em memória (ex: `@st.cache_data(ttl=3600)` no Streamlit) utilizando a chave `(latitude, longitude, start_date, end_date, past_days)` para evitar chamadas duplicadas idênticas durante a navegação do usuário.