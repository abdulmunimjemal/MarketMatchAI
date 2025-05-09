# syntax=docker/dockerfile:1
FROM python:3.11-slim

# set working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# install Poetry
RUN pip install --upgrade pip poetry

# copy dependency definitions
COPY pyproject.toml poetry.lock* ./

# install Python dependencies without creating venv
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi 

# copy application code
COPY . .

# expose port and define environment
ENV FLASK_APP=main.py
ENV FLASK_ENV=production
EXPOSE 5000

# run with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
