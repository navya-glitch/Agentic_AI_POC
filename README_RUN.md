How to run (Windows PowerShell)

1) Activate the virtual environment

```powershell
& .\.venv\Scripts\Activate.ps1
```

2) Change to the app folder

```powershell
Set-Location .\insurance_agentic_poc
```

3) Run Streamlit (recommended — avoids broken launcher)

```powershell
python -m streamlit run .\ui_dynamic_fixed.py
```

4) To bind explicitly to localhost on port 8501

```powershell
python -m streamlit run .\ui_dynamic_fixed.py --server.address 127.0.0.1 --server.port 8501
```

5) If the `streamlit` launcher shows a "Unable to create process" error, force-reinstall Streamlit

```powershell
python -m pip install --upgrade --force-reinstall streamlit
```

That's it — run the first 3 commands to start the app.
