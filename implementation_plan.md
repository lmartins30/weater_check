# Plano de Melhoria de UX e Regras de Negócio (V2)

O objetivo desta refatoração é transformar dados estatísticos crus em respostas de negócio claras. A pergunta principal a ser respondida pelo Dashboard agora é: **"Até qual dia no futuro eu posso confiar na previsão atual?"**

---

## 1. Tradução da "Matriz de Confusão" (Precipitação)
Vamos remover a sopa de letrinhas técnica e usar termos reais de impacto:
- **VP (Verdadeiro Positivo) ➔ "Chuva Prevista e Confirmada"**: O modelo disse que choveria e choveu.
- **VN (Verdadeiro Negativo) ➔ "Dias de Sol Acertados"**: O modelo disse que não choveria e fez sol.
- **FP (Falso Positivo) ➔ "Alarme Falso"**: O modelo prometeu chuva, mas fez sol (frustrou quem desmarcou o passeio).
- **FN (Falso Negativo) ➔ "Chuva Surpresa"**: O modelo prometeu sol, mas choveu (molhou quem saiu sem guarda-chuva).

> **Ação:** Substituímos as métricas por cards coloridos (Verde para acertos, Vermelho/Laranja para os erros) e adicionamos a métrica de "Confiabilidade Geral de Chuva" (Acertos Totais / Dias Totais).

## 2. Esclarecimento da Acurácia de Temperatura
- Foi adicionado um card explicativo simples: *"Qual a porcentagem de vezes que o modelo errou por, no máximo, 2°C (para mais ou para menos)?"*
- Destacamos o maior erro de temperatura (diferença de graus) e em qual dia/hora ele ocorreu.

## 3. O Novo Gráfico: Horizonte de Confiança (Lead Time)
Para responder "até qual dia posso confiar?", criamos a métrica de **Decaimento da Previsão**:
1. Criamos um gráfico de linha onde o Eixo X é "Dias de Antecedência" (1 a 7 dias) e o Eixo Y é a "Acurácia %".
2. **Simulação Pedagógica:** Como a API gratuita não nos fornece *histórico de previsões*, criamos uma simulação realista atrelada aos dados reais para fins de demonstração.
3. **Limiar de Confiança:** Traçamos uma linha vermelha horizontal no limite de `70%`. Onde a linha de acurácia cruza para baixo, exibimos um alerta gigante avisando até qual dia a previsão é segura.

## 4. UI/UX "Premium"
- Uso de `st.expander` para esconder configurações técnicas.
- Uso de colunas `st.columns` proporcionais para criar um estilo de "Cockpit".
- Gráficos Plotly com legendas mais limpas.
