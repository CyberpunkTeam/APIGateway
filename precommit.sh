pip install poetry

poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
pip install pre-commit
pre-commit install
pre-commit run
