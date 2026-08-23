@echo off
cd /d "%~dp0"
echo ==============================================
echo Iniciando o Dashboard de Avaliacao de Previsoes
echo ==============================================

if not exist "venv\Scripts\python.exe" (
    echo [ERRO] O ambiente virtual "venv" nao foi encontrado!
    echo Certifique-se de instalar as dependencias primeiro.
    pause
    exit /b 1
)

echo Ativando ambiente virtual e configurando caminhos...
set PYTHONPATH=%cd%

echo Subindo o servidor do Streamlit...
venv\Scripts\python.exe -m streamlit run src\app\app.py

pause
