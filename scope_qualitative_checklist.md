# Checklist Qualitativo e Critérios de Aceite

## 1. Padrões de Código Python
- [ ] Estilo PEP 8 seguido rigorosamente (ex: snake_case para variáveis, limite de 79/99 caracteres), verificado por `black` ou `ruff`.
- [ ] Funções e classes contêm Type Hints (PEP 484) nas assinaturas e retornos.
- [ ] Toda função pública possui Google Docstring descrevendo Args, Returns e Raises.
- [ ] Exclusão completa de `print()` em favor da biblioteca padrão `logging` (usando níveis INFO, WARNING, ERROR).
- [ ] Tratamento de exceções específicas (ex: `ValueError`, `requests.exceptions.Timeout`), evitando cláusulas `except Exception:` genéricas.

## 2. Testes Automatizados (Pytest)
- [ ] **Testes de API e Geocodificação:** Mocks validando comportamentos para timeouts, CEPs inválidos e extração correta de Lat/Lon.
- [ ] **Testes de Fuso Horário e Dados:** Verificação assertiva de que os painéis (Previsto vs. Real) se unem perfeitamente por hora local.
- [ ] **Testes de Regras de Negócio:** Funções de cálculo de erro, interpolação de NaNs e threshold de chuva validadas com asserts unitários.

## 3. Engenharia de Projeto
- [ ] Código modular: Separação clara entre a pipeline de dados, chamadas de rede e interface (Streamlit).
- [ ] Dependências isoladas em ambiente virtual (venv, poetry) e devidamente travadas em `requirements.txt`.