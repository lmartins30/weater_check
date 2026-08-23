# Dashboard de Avaliação de Previsões Meteorológicas - Plano de Implementação

Este plano divide a construção do projeto em 3 fases principais baseadas na estrutura sugerida. Ele foi elaborado para seguir rigorosamente os guias de desenvolvimento contidos nos arquivos `.md` do repositório.

---

## Fase 1: Integrações Externas (`src/api`)
Foco na robustez das chamadas de rede, resiliência e contratos de dados.

### 1.1 BrasilAPI (Geolocalização via CEP)
- [ ] Criar o arquivo `src/api/brasil_api.py`.
- [ ] Implementar a função para consumir o endpoint de CEP `v2`.
- [ ] Configurar mecanismo de **Exponential Backoff** com a biblioteca `tenacity` (máx. 3 tentativas exclusivas para erros `5xx` e timeouts).
- [ ] Criar exceções customizadas: `CEPNotFoundError` (para HTTP 404) e `CEPTimeoutError` (timeout após 10s).
- [ ] Extrair estritamente `latitude` e `longitude` do JSON.
- [ ] Criar o arquivo `tests/test_brasil_api.py` com mocks usando `pytest` para simular falhas e sucesso.

### 1.2 Open-Meteo (Dados Climáticos)
- [ ] Criar o arquivo `src/api/open_meteo.py`.
- [ ] Configurar a função base para `archive-api.open-meteo.com` exigindo obrigatoriamente o parâmetro `timezone`.
- [ ] Definir o schema `Pydantic` para o contrato de resposta, garantindo e tolerando as chaves: `time`, `temperature_2m` (NaN/None) e `precipitation` (NaN/None).
- [ ] Garantir que o tamanho do array de tempo é igual ao das variáveis.
- [ ] Criar `tests/test_open_meteo.py` com mocks para testar se a validação Pydantic funciona conforme esperado.

---

## Fase 2: Processamento e Métricas (`src/pipeline`)
Foco na limpeza dos dados e aplicação das regras de negócio do domínio.

### 2.1 Tratamento de Dados (Cleaning)
- [ ] Criar arquivo `src/pipeline/cleaning.py` (usando Pandas ou Polars).
- [ ] Implementar função que preenche valores nulos de **Precipitação** com `0.0`.
- [ ] Implementar função para tratar **Temperatura**: interpolar linearmente buracos de até 2 horas consecutivas; dropar buracos maiores.
- [ ] Criar testes unitários para confirmar que os buracos de dados são tratados corretamente.

### 2.2 Cálculos de Regras de Negócio
- [ ] Criar arquivo `src/pipeline/metrics.py`.
- [ ] Implementar o filtro da Janela de Previsão (Lead Time).
- [ ] Função para calcular o **Erro Absoluto** da temperatura e sinalizar acertos (erro <= 2°C).
- [ ] Função para gerar a **Matriz de Confusão de Precipitação** (VP, FP, FN, VN), considerando o limite de chuva `> 0.1mm`.
- [ ] Testes exaustivos com dados sintéticos no `pytest` para garantir a precisão dos cálculos.

---

## Fase 3: Interface Web (`src/app`)
Foco na Experiência do Usuário (UX) e visualização com Streamlit.

### 3.1 Camada de Cache
- [ ] Implementar decorador `@st.cache_data` envolvendo a chamada da Open-Meteo usando as chaves `(latitude, longitude, start_date, end_date, past_days)`.

### 3.2 Componentes Visuais e Fluxo
- [ ] Criar `src/app/app.py`.
- [ ] Inserir input de CEP com tratamento amigável (capturar a `CEPNotFoundError` da Fase 1 e exibir alerta amarelo sem quebrar o app).
- [ ] Construir layout para exibir a matriz de confusão.
- [ ] Plotar gráficos dinâmicos temporais usando `plotly` cruzando a curva da temperatura real com a curva prevista, realçando os acertos/erros.
