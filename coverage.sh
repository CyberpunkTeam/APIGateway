pip install poetry

poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

coverage run --source=app -m pytest tests/

curl -Os https://uploader.codecov.io/latest/linux/codecov

chmod +x codecov
./codecov
