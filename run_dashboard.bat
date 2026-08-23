@echo off
echo ==============================================
echo Iniciando o Dashboard de Avaliacao de Previsoes
echo ==============================================

if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] O ambiente virtual (venv) nao foi encontrado!
    echo Certifique-se de instalar as dependencias primeiro.
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Subindo o servidor do Streamlit...
streamlit run src\app\app.py

pause
