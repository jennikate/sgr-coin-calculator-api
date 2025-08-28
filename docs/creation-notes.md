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
- run `flask db init`
- run `flask db migrate -m "Initial migration"`
- check migration version file and ensure happy
- run `flask db upgrade`

** don't forget to `import models` into `app.py`
