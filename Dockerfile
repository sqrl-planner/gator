FROM python:3.9.0-slim-buster AS app

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential curl libpq-dev \
  && apt-get install -y git \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && chown python:python -R /app

RUN chmod -R 777 /usr/local/src

USER python

COPY --chown=python:python pyproject.toml ./
COPY --chown=python:python poetry.lock ./

COPY --chown=python:python bin/ ./bin

# System dependencies
RUN chmod 0755 bin/* && bin/poetry-install

ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    FLASK_APP="gator.app" \
    FLASK_SKIP_DOTENV="true" \
    PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

COPY --chown=python:python . .

RUN if [ "${FLASK_ENV}" != "development" ]; then \
  ln -s /public /app/public && rm -rf /app/public; fi

EXPOSE 5000

# Project dependencies
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-interaction --no-ansi

CMD ["gunicorn", "-c", "python:config.gunicorn", "gator.app:create_app()"]
