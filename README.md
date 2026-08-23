# Dashboard de Avaliação de Previsões Meteorológicas

Aplicação web interativa desenvolvida em Python para avaliar a precisão de previsões meteorológicas históricas, cruzando dados previstos com dados reais. O projeto segue padrões rigorosos de engenharia de software e MLOps.

## 🚀 Tecnologias e Stack

- **Linguagem:** Python (com Type Hints obrigatórios)
- **Interface Web:** Streamlit
- **Visualização de Dados:** Plotly
- **Manipulação de Dados:** Pandas / Polars
- **Validação de Dados:** Pydantic
- **Testes e Qualidade:** Pytest, Black, Ruff, Isort
- **APIs:** BrasilAPI (Geolocalização) e Open-Meteo (Clima histórico e previsões)

## 📁 Estrutura do Projeto

```text
├── src/
│   ├── api/          # Integrações (BrasilAPI, Open-Meteo)
│   ├── pipeline/     # Processamento, limpeza e cálculos de métricas
│   └── app/          # Interface Streamlit principal (app.py)
├── tests/            # Testes unitários e de integração
├── requirements.txt  # Dependências do projeto
├── pyproject.toml    # Configuração de ferramentas (Black, Ruff, Isort, Pytest)
└── README.md
```

## 🛠️ Como executar localmente

1. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/Mac:
   source venv/bin/activate
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação (a ser desenvolvida):
   ```bash
   streamlit run src/app/app.py
   ```
