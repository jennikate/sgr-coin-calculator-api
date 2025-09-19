# Install and Run Backend/API

# Development

## Creating and activating virtual environment

Create a venv
```bash
python -m venv .venv
```

Activate the venv
```bash
source  .venv/bin/activate
```

## Install dependencies

Install dependencies
```bash
uv pip install -r requirements.txt
```

## Setup your .env file

DEBUG=True
FLASK_ENV=development

DBUSER=[request or create]
DBPASSWORD=[request or create]
DBHOST=localhost
DBPORT=5432
DBNAME=[request or create]


## Run app locally

```bash
uv run python run.py
```


## Creating and updating the db

Note commands below are because I am using `uv` and a `src` folder structure.

- create a postgres db `createdb -U <username> <namefordb>`
- setup SQLAlchemy config 
- setup env vars for 
```bash
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
DATABASE_URL=postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
```
- setup model(s)
- run `uv run flask --app run:app db init`
- run `uv run flask --app run:app db migrate -m "Initial migration"`
- check migration version file and ensure happy
- run `uv run flask --app run:app db upgrade`

Initial database seed
We need to add the default rank to the database. This should exist as a migration named *_add_default_rank.py

To recreate it
- create an alembic migration by running `uv run flask --app run:app db migrate -m "Add default rank"`
- in your IDE remove the Alembic generated upgrade/downgrade details and replace with the code from [database_seed](./database-seed.md)
- It is important that the DEFAULT_RANK values in the database_seed are the same as the DEFAULT_RANK values in the constants file.
- Save your changes
- run `uv run flask --app run:app db upgrade`


Future migrations
- run `uv run flask --app run:app db migrate -m "<description>"`
- check migration version file and ensure happy
- run `uv run flask --app run:app db upgrade`

** don't forget to `import models` into `app.py`
