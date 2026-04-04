# Streamlit Data App

This project currently includes a minimal Streamlit starter app in `app.py`.

## Run locally

1. Use the project virtual environment based on Python 3.13:

   ```powershell
   .\.venv313\Scripts\Activate.ps1
   ```

2. Start the app:

   ```powershell
   python -m streamlit.web.cli run app.py
   ```

If you need to reinstall dependencies into this environment:

   ```powershell
   C:\Users\ADMIN\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt --target .\.venv313\Lib\site-packages
   ```

## Why the current environment fails

The existing `.venv` uses Python 3.14.2. `streamlit` is not available for that interpreter in this environment, so `pip install streamlit` fails there.
