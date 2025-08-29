# Creation Notes
Reference notes made during creation that are things I want to remember.

## Contents






----

## Flask App creation with uv

The app is bootstrapped and managed with [uv](https://docs.astral.sh/uv/guides/projects/#creating-a-new-project)

To create the initial app:
```bash
uv init
```

We then just add Flask as a package so we can use it
```bash
uv add flask
```

---

## Adding / Managing dependencies

To add dependencies

```bash
uv add <name>
```
or
```bash
uv add <name> --dev
```

To remove one
```bash
uv remove <name>
```

----

## Creating the db

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

** don't forget to `import models` into `app.py`

Future migrations
- run `uv run flask --app run:app db migrate -m "<description>"`
- check migration version file and ensure happy
- run `uv run flask --app run:app db upgrade`

----

## Using a src folder

Put most of the create_app and configuration to the __init__.py within the src folder as this is what you call to run the package.

The run.py file will call the create_app() from the src folder (what is in the __init__.py).

Can also add the `logger` and the `CORS` setup to the run.py file.

