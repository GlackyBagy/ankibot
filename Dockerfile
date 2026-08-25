FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY *.py ./
COPY middleware/ ./middleware/
COPY web/ ./web/

ENTRYPOINT ["uv", "run", "main.py"]
