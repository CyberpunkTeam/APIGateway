pip install poetry

poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

coverage run --source=app -m pytest tests/

coveralls
