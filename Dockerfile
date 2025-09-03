# Use uv’s official Python base with uv preinstalled
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

# Copy only dependency files for dependency resolution
COPY pyproject.toml uv.lock README.md ./
RUN uv pip install --system --no-deps -e .

# Now copy the source code
COPY . .

# Install project in editable mode with deps
RUN uv pip install --system -e .

ENV PYTHONPATH=/app
CMD ["pytest", "-v"]
