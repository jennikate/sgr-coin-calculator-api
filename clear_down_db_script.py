import os
import shutil
import subprocess
from sqlalchemy import create_engine, text

# ------------------------
# CONFIGURATION
# ------------------------
DB_NAME = "db_name"
DB_USER = "user_name"
DB_PASS = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

MIGRATIONS_FOLDER = "migrations"
FLASK_APP_MODULE = "app.py"  # change if your app entry point is different

# ------------------------
# DROP DATABASE
# ------------------------
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/postgres")

with engine.connect() as conn:
    conn.execute(text("COMMIT"))
    conn.execute(text(f"DROP DATABASE IF EXISTS {DB_NAME}"))
    conn.execute(text(f"CREATE DATABASE {DB_NAME}"))

print(f"[INFO] Database '{DB_NAME}' dropped and recreated.")

# ------------------------
# DELETE MIGRATIONS FOLDER
# ------------------------
if os.path.exists(MIGRATIONS_FOLDER):
    shutil.rmtree(MIGRATIONS_FOLDER)
    print(f"[INFO] Deleted '{MIGRATIONS_FOLDER}' folder.")

# ------------------------
# RE-INITIALIZE ALEMBIC
# ------------------------
os.environ["FLASK_APP"] = FLASK_APP_MODULE

subprocess.run(["uv", "run", "flask", "--app", "run:app", "db", "init"], check=True)
print("[INFO] Alembic migrations folder re-initialized.")

# ------------------------
# CREATE INITIAL MIGRATION
# ------------------------
subprocess.run(["uv", "run", "flask", "--app", "run:app", "db", "migrate", "-m", "Initial migration"], check=True)
print("[INFO] Initial migration created.")

# ------------------------
# APPLY MIGRATION
# ------------------------
subprocess.run(["uv", "run", "flask", "--app", "run:app", "db", "upgrade"], check=True)
print("[INFO] Database upgraded with initial migration.")

print("[SUCCESS] Database and migrations fully reset!")
