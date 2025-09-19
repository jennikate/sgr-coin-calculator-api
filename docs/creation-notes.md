# Creation Notes
Reference notes made during creation that are things I want to remember.

## Contents

- [Flask App creation with uv](#flask-app-creation-with-uv)
- [Adding / Managing dependencies](#adding--managing-dependencies)
- [Using a src folder](#using-a-src-folder)

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

Updating requirements.txt
```bash
uv pip freeze > requirements.txt
```

----

## Using a src folder

Put most of the create_app and configuration to the __init__.py within the src folder as this is what you call to run the package.

The run.py file will call the create_app() from the src folder (what is in the __init__.py).

Can also add the `logger` and the `CORS` setup to the run.py file.

