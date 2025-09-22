#!/bin/bash
set -e

# Use your environment variables from .env
export PGPASSWORD="$DBPASSWORD"

echo "Waiting for Postgres at $DBHOST:$DBPORT..."

# Timeout setup (60 seconds)
timeout=60
counter=0

until pg_isready -h "$DBHOST" -p "$DBPORT" -U "$DBUSER"; do
  sleep 1
  counter=$((counter+1))
  if [ $counter -ge $timeout ]; then
    echo "Postgres did not start within $timeout seconds."
    exit 1
  fi
done

echo "Postgres is ready. Running migrations..."
uv run flask --app run:app db upgrade


echo "Starting Flask app..."
if [ "$FLASK_ENV" = "production" ]; then
    # Production: Gunicorn
    exec uv run gunicorn -w 4 -b 0.0.0.0:5000 run:app
else
    # Development: Flask dev server / uv
    exec uv run python "$FLASK_APP"
fi