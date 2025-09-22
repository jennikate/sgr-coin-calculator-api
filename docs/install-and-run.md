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
uv sync
```

## Setup your .env file
Recommended: 
- `.env.docker` for developing in Docker
- `.env.local` so you can develop locally without Docker if you prefer
- `.env.prod` so you can test production settings (in Docker)

```bash
# APP
FLASK_APP=run.py
FLASK_ENV=development # can be: development, production, staging, testing
SECRET_KEY=some-string-for-dev
# If SECRET_KEY is missing in prod, Flask will auto-generate a strong key at startup. (see secrets.token_hex(32) in the create_app code)
# or can set one we want here, but make sure to keep the production secret key random and long (e.g., openssl rand -hex 32).

# LOGGING
FLASK_DEBUG=0 # 1 debug on, 0 debug off
LOG_LEVEL=DEBUG # levels used: DEBUG, INFO, WARNING, ERROR, CRITICAL

# DB
DBUSER=[request or create]
DBPASSWORD=[request or create]
DBHOST=[request or create] # matches the Docker service name, use localhost for local dev
DBPORT=5432
DBNAME=[request or create]

POSTGRES_USER=${DBUSER}
POSTGRES_PASSWORD=${DBPASSWORD}
POSTGRES_DB=${DBNAME}
```

## Running app

You can use the `run.sh` to set the variables and run in your chosen environment.
Or you can do it manually (see sections below).

_Note: you may need to make this script executable with `chmod +x run.sh`_

To run replace `local` with `docker` for Docker dev, or `prod` for production settings.
```bash
./run.sh local
```

### Run app locally
This uses a local Postgres and sets debug=True, log_level=DEBUG

You set your env to use `.env.local` then start the app.

```bash
uv run python run.py
```

### Run app with Docker in development mode
This uses a Docker Postgres, sets debug=True, log_level=DEBUG and has a hot reload.
The docker-compose.yml defaults to docker/dev so no need to specify Dockerfile.dev

```bash
docker-compose down -v                           
docker-compose up --build
```
docker-compose down -v: -v ensures the Postgres volume is reset so the correct database is created.


### Run app with Docker in production mode
This uses a Docker Postgres and sets debug=False, log_level=INFO and uses Gunicorn
```bash
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build
```


TODO: investigate using Gunicorn
_Note: Gunicorn: a production ready WSGI (Web Server Gateway Interface) that handles multiple requests using multiple worker processes simultaneously, improving performance._
_WSGI is a standard interface that enables Python applications and frameworks to communicate with web servers._


## Creating and updating the db

Note commands below are because I am using `uv` and a `src` folder structure.

- create a postgres db `createdb -U <username> <namefordb>`
- setup SQLAlchemy config 
- setup env vars for 
```bash
DBUSER=
DBPASSWORD=
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
