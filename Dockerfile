FROM python:3.9-slim

RUN pip install poetry
COPY poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
  && poetry install --without dev --no-interaction --no-ansi

WORKDIR /users
COPY ./ ./

CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT_APP
