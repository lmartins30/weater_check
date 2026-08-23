# Escopo do Projeto: Dashboard de Avaliação de Previsões Meteorológicas

## 1. Visão Geral
Desenvolvimento de uma aplicação web interativa em Python para avaliar a precisão de previsões meteorológicas históricas. O projeto deve seguir padrões rigorosos de engenharia de software e MLOps.

## 2. Arquitetura e Stack Tecnológico
- **Linguagem:** Python (Tipagem estática obrigatória via Type Hints)
- **Interface Web:** Streamlit
- **Visualização de Dados:** Plotly
- **Manipulação de Dados:** Pandas / Polars
- **Validação de Dados:** Pydantic
- **Testes e Qualidade:** Pytest, Black, Ruff, Isort

## 3. Estrutura de Diretórios Recomendada
```text
├── src/
│   ├── api/          # Integrações (BrasilAPI, Open-Meteo)
│   ├── pipeline/     # Processamento, limpeza e cálculos
│   └── app/          # Interface Streamlit (app.py)
├── tests/            # Testes unitários e de integração (pytest)
├── requirements.txt  # Dependências com versões fixadas
└── README.md