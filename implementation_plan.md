# Plano de Expansão V3: Ventos, Umidade e Sistema Inteligente de Alertas

Para dar muito mais valor ao Dashboard, vamos expandir a coleta de dados da Open-Meteo e transformar esses dados brutos em **Alertas Automáticos** para o usuário.

---

## 1. Expansão da API (`src/api/open_meteo.py`)
A API da Open-Meteo possui centenas de parâmetros. Para o nosso contexto de negócio, adicionaremos:
- **`wind_speed_10m`**: Velocidade do Vento a 10 metros do solo (km/h).
- **`relative_humidity_2m`**: Umidade Relativa do Ar (%).

**Ações Técnicas:**
- Adicionar essas chaves na URL da requisição.
- Atualizar o `Pydantic Schema` (o contrato) para garantir que as listas de vento e umidade também venham no tamanho correto e validar seus tipos.

## 2. Motor de Alertas (`src/pipeline/alerts.py`)
Como a API histórica não devolve "textos de alerta" governamentais nativos, nós mesmos criaremos as nossas regras de negócio (Sistema Especialista):
- **🌬️ Alerta de Ventania:** Se a previsão cruzar a linha de `50 km/h`.
- **🌵 Alerta de Tempo Seco:** Se a umidade ficar abaixo de `20%` (Risco à saúde).
- **🔥/❄️ Alerta de Risco Térmico:** Se a temperatura prever bater mais de `35°C` ou menos que `5°C`.

**Ações Técnicas:**
- Criar a função `generate_alerts(df)` que varre o DataFrame procurando por picos que acionem essas regras e retorna uma lista de avisos com o dia e hora de ocorrência.
- Escrever testes unitários em `tests/test_alerts.py`.

## 3. Visualização na Interface (`src/app/app.py`)
- **Painel de Alertas:** Exibir uma tarja vermelha/amarela no topo do dashboard caso a função detecte algum risco iminente naquela semana.
- **Gráfico Secundário (Vento/Umidade):** Um novo gráfico de linhas com 2 eixos Y, mostrando as oscilações da Umidade (em azul) e os picos de Vento (em cinza).
