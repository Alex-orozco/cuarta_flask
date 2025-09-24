@echo off
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
python init_db.py
python app.py
pause
