# Copyright (c) 2022 Joseph Hale
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

# Default to the latest bookworm version of Python at the time of writing 3.11.4
ARG PYTHON_IMAGE_TAG=3.11.4-bookworm

###############################################################################
# POETRY BASE IMAGE - Provides environment variables for poetry
###############################################################################
FROM python:${PYTHON_IMAGE_TAG} AS python-poetry-base

# Add some base setup ENVs
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Default to the latest version of Poetry
ARG POETRY_VERSION=""

ENV POETRY_VERSION=${POETRY_VERSION}
ENV POETRY_HOME="/opt/poetry"
ENV CACHE_DIR = "$POETRY_HOME/cache"
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VIRTUALENVS_PATH = "$CACHE_DIR/virtualenvs"
ENV PATH="$POETRY_HOME/bin:$PATH"


###############################################################################
# POETRY BUILDER IMAGE - Installs Poetry and dependencies
###############################################################################
FROM python-poetry-base AS python-poetry-builder
RUN apt-get update
RUN apt-get upgrade --yes
RUN apt-get install curl --yes
# Install Poetry via the official installer: https://python-poetry.org/docs/master/#installing-with-the-official-installer
# This script respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

###############################################################################
# POETRY RUNTIME IMAGE - Copies the poetry installation into a smaller image
###############################################################################
FROM python-poetry-base AS python-poetry
COPY --from=python-poetry-builder $POETRY_HOME $POETRY_HOME

ENV FASTAPI_ENV=production

# Set workdir and copy project files
WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN poetry config virtualenvs.path /opt/poetry/cache/virtualenvs
RUN poetry install
COPY gunicorn_conf.py /gunicorn_conf.py
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
COPY . .

EXPOSE 3682
ENTRYPOINT /docker-entrypoint.sh $0 $@
# CMD ["uvicorn", "--reload", "main:app"]
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app"]