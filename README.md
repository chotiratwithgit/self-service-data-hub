# Self-Service Data Hub

A Streamlit dashboard for internal team use, built to connect to brewery data stored in Supabase PostgreSQL. The app allows users to explore data, run standard reports, download filtered datasets, and review data quality issues from a single interface.

## Overview

This project is designed as a self-service analytics tool to reduce ad hoc data requests. Team members can use the dashboard to:

- View high-level brewery dataset summaries
- Search and filter data by `brewery_type` and `state_name`
- Download filtered data as CSV
- Use standard saved reports
- Review records with data quality issues
- Monitor pipeline and application health

## Data Source

The app connects to Supabase PostgreSQL using SQLAlchemy and reads the database connection string from an environment variable:

```env
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

Current source table:

```sql
SELECT * FROM dbt_chotiratwithgit_public.stg_breweries
```

Expected schema:

- `id`
- `brewery_name`
- `brewery_type`
- `city`
- `state_name`
- `country`

## App Features

### 1. Executive Overview

Provides a summary of the brewery dataset, including:

- Total brewery count
- Number of brewery types
- Number of states covered
- Number of countries covered
- Breweries by type chart
- Top states chart
- Top cities table

### 2. Data Explorer

Designed for internal users who want to explore data directly:

- Filter by `brewery_type`
- Filter by `state_name`
- Search by `brewery_name`
- Preview filtered results in a table

### 3. Data Download

Allows users to export filtered records:

- Select columns to export
- Preview export data before download
- Download filtered data as CSV

### 4. Saved Reports

Provides standard recurring reports:

- Breweries by type
- Breweries by state
- Top cities by brewery count

### 5. Quarantine

Performs basic data quality checks such as:

- Missing ID
- Missing Brewery Name
- Missing Brewery Type
- Missing City
- Missing State Name
- Missing Country
- Duplicate ID

### 6. Pipeline Health

Displays simple monitoring information:

- Total records
- Valid records
- Quarantine records
- Last refresh timestamp
- Basic system logs

## Tech Stack

- `Streamlit`
- `Pandas`
- `SQLAlchemy`
- `psycopg2-binary`
- `python-dotenv`
- `Supabase PostgreSQL`

## Project Structure

```text
Streamlit (Data App)/
|-- app.py
|-- requirements.txt
|-- run_app.ps1
|-- .gitignore
|-- README.md
```

## Local Setup

### 1. Create and activate a virtual environment

Example using Python 3.13:

```powershell
python -m venv .venv313
.\.venv313\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

If `pip` is not available inside the virtual environment, install packages directly with Python 3.13:

```powershell
C:\Users\ADMIN\AppData\Local\Programs\Python\Python313\python.exe -m pip install -r requirements.txt --target .\.venv313\Lib\site-packages
```

### 3. Create `.env`

Create a `.env` file in the project root:

```env
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@db.xxxxx.supabase.co:5432/postgres
```

Notes:

- Do not commit `.env` to GitHub
- The connection string must point to a database containing `dbt_chotiratwithgit_public.stg_breweries`

### 4. Run the app

Run through PowerShell:

```powershell
.\run_app.ps1
```

Or run directly:

```powershell
.\.venv313\Scripts\python.exe -m streamlit.web.cli run app.py
```

If you are using another environment with `streamlit.exe`:

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

Then open:

```text
http://localhost:8501
```

## Requirements

Current dependencies in `requirements.txt`:

```txt
streamlit
pandas
sqlalchemy
python-dotenv
psycopg2-binary
supabase
```

Note: the current app primarily uses SQLAlchemy to read from Supabase PostgreSQL. The `supabase` package is included but is not currently used directly in `app.py`.

## Notes

- This repository is intended for internal team usage
- If the database schema changes, update the column references in `app.py`
- If `SUPABASE_DB_URL` is missing, the app will not be able to connect to the database
- If the table or schema name changes, update the SQL query inside `get_brewery_data()`

## Future Improvements

- Add global filters shared across all tabs
- Add refresh metadata and load timestamps
- Support Excel export
- Add more interactive charts
- Add deployment and access-control options for internal users
