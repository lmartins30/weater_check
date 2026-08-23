# Regras de Negócio e Cálculos de Métricas

## 1. Tratamento de Dados Faltantes (NaNs / Nulls)
A API pode retornar dados ausentes pontuais. A esteira deve processá-los da seguinte forma:
- **Precipitação:** Preencher valores nulos com `0.0` (assumir ausência de chuva).
- **Temperatura:** 
  - Lacunas de até 2 horas consecutivas: Aplicar interpolação linear.
  - Lacunas maiores que 2 horas: Descartar a linha (`dropna`) para evitar que dados sintéticos interfiram na acurácia do erro.

## 2. Regras de Cálculo
- **Janela de Previsão (Lead Time):** Avaliar previsões geradas X dias antes da data alvo.
- **Erro Absoluto de Temperatura:** `|Temperatura_Real - Temperatura_Prevista|`.
- **Critério de Acerto de Temperatura:** Erro absoluto menor ou igual a 2°C.

## 3. Matriz de Confusão (Precipitação)
- **Limiar de Chuva:** Considerar ocorrência de chuva se `precipitacao > 0.1` mm.
- **Métricas:**
  - **VP (Verdadeiro Positivo):** Previu chuva e choveu.
  - **FP (Falso Positivo):** Previu chuva e não choveu.
  - **FN (Falso Negativo):** Previu sem chuva e choveu.
  - **VN (Verdadeiro Negativo):** Previu sem chuva e não choveu.