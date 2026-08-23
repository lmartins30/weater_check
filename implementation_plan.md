# Plano de Expansão V3.1: Ventos e Umidade na Análise de Confiabilidade

Atendendo ao pedido, removemos a ideia do sistema de alertas avulso e vamos tratar o Vento e a Umidade exatamente da mesma forma que tratamos a Chuva: avaliando a **Confiabilidade da Previsão** através de métricas de acerto e erro.

---

## 1. Expansão da API e Limpeza (`src/api` e `src/pipeline`)
- Adicionar **`wind_speed_10m`** e **`relative_humidity_2m`** na chamada da Open-Meteo.
- Atualizar o `Pydantic Schema` para as novas listas.
- Estender as rotinas de limpeza no Pandas para preencher eventuais buracos nesses dados novos (ex: usar a mesma lógica de interpolação da temperatura).

## 2. Simulação e Métricas (`src/pipeline/metrics.py`)
- Gerar simulações sintéticas (adicionando ruído) para as previsões de Vento e Umidade, já que não temos previsões reais do passado.
- Expandir a função de Matriz de Confusão para suportar o cálculo de acurácia de Vento e Umidade, utilizando os pontos de corte definidos (15km/h e 40%).

## 3. Interface Visual (`src/app/app.py`)
Vamos adicionar duas novas seções ao Dashboard que seguirão exatamente o mesmo padrão de design que usamos para a Chuva (com os 4 quadrantes):

- **Confiabilidade do Vento (limite: 15 km/h)**
  - ✅ **Acertou o Vento**: Previu vento forte e ventou.
  - 🍃 **Acertou Calmaria**: Previu pouco vento e assim foi.
  - ❌ **Alarme Falso (Vento)**: Previu vento forte, mas não ventou.
  - 💨 **Vento Surpresa**: Previu calmaria, mas ventou forte.

- **Confiabilidade da Umidade (Tempo Seco < 40%)**
  - ✅ **Acertou Tempo Seco**: Previu seco e foi seco.
  - 💧 **Acertou Tempo Úmido**: Previu umidade normal e assim foi.
  - ❌ **Alarme Falso (Seca)**: Previu seco, mas ficou úmido.
  - 🌵 **Seca Surpresa**: Previu umidade normal, mas ficou seco.
