FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.4.1"

COPY pyproject.toml poetry.lock ./

# Install only what the service needs — PyQt6 is never touched
RUN poetry install --only services,shared --no-root

COPY dash-services/ ./

EXPOSE 8080
CMD ["poetry", "run", "python", "main.py"]
