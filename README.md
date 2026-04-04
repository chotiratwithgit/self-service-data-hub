# Self-Service Data Hub

Streamlit dashboard for exploring brewery data from Supabase PostgreSQL. This repository is set up to be deployed on Streamlit Cloud.

## What It Does

- Shows a high-level brewery overview
- Lets users filter and search brewery records
- Supports CSV download of filtered data
- Includes saved report views
- Highlights data quality issues
- Shows simple pipeline health metrics

## Data Source

The app queries this table:

```sql
SELECT * FROM dbt_chotiratwithgit_public.stg_breweries
```

Expected columns:

- `id`
- `brewery_name`
- `brewery_type`
- `city`
- `state_name`
- `country`

## Deploy On Streamlit Cloud

### 1. Push this repository to GitHub

Make sure these files are present:

- `app.py`
- `requirements.txt`
- `README.md`

Do not commit secret files such as `.env` or `.streamlit/secrets.toml`.

### 2. Create the app in Streamlit Cloud

In Streamlit Cloud:

1. Click `New app`
2. Select this GitHub repository
3. Set the main file path to `app.py`
4. Deploy

### 3. Add app secrets

After the app is created, open:

`App settings` > `Secrets`

Add:

```toml
SUPABASE_DB_URL = "postgresql://postgres:YOUR_PASSWORD@HOST:PORT/postgres"
```

Notes:

- The key name must be exactly `SUPABASE_DB_URL`
- Do not wrap the whole file in JSON
- Save the secrets and reboot the app after updating them

### 4. Confirm database access

The connection string must point to a Supabase PostgreSQL instance that contains:

- schema: `dbt_chotiratwithgit_public`
- table: `stg_breweries`

If the secret is missing, the app will stop and show a setup message on screen.

## Requirements

Dependencies from `requirements.txt`:

```txt
streamlit
pandas
sqlalchemy
python-dotenv
psycopg2-binary
supabase
```

`python-dotenv` is kept for optional local development, but Streamlit Cloud uses `st.secrets` for production deployment.

## Local Development

Local run is optional. If needed, create a `.env` file in the project root:

```env
SUPABASE_DB_URL=postgresql://postgres:YOUR_PASSWORD@HOST:PORT/postgres
```

Then run:

```powershell
streamlit run app.py
```

## Troubleshooting

### App says `SUPABASE_DB_URL` is missing

Check that:

- the secret is added in Streamlit Cloud
- the key name is exactly `SUPABASE_DB_URL`
- the app was rebooted after saving secrets

### App deploys but cannot query data

Check that:

- the database URL is valid
- the database is reachable from Streamlit Cloud
- the target table exists
- the expected columns still exist

## Security

- Never commit `.env`
- Never commit `.streamlit/secrets.toml`
- If a real credential was committed previously, rotate it in Supabase

## Next Phase

The next phase of this project will focus on data governance to improve data quality, accountability, and trust across the platform.
