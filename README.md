# SGR Coin Calculator API
The backend and API for the SGR Coin Calculator

## Requirements

- Python 3.13
- Flask
- uv



## Setup, install, build notes

### Creating and activating virtual environment

Create a venv
- `python -m venv .venv`

Activate the venv
- `source  .venv/bin/activate`

### Install dependencies



----

### Initial creation with

- `uv init`

### Add new dependencies

- `uv add <name>`
- `uv add <name> --dev`


----

### creating the db

- create a postgres db `createdb -U <username> <namefordb>`
- setup SQLAlchemy config 
- setup env vars for 
```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DATABASE_URL=postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```
- setup model(s)
- run `flask db init`
- run `flask db migrate -m "Initial migration"`

** don't forget to `import models` into `app.py`