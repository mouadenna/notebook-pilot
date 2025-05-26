@echo off
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo Setup complete! Virtual environment is ready to use.
echo To activate the environment, run: venv\Scripts\activate.bat 