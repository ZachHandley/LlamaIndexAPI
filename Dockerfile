# Default to the latest bookworm version of Python at the time of writing 3.11.4
ARG PYTHON_IMAGE_TAG=3.11.4-slim-1.6.1

###############################################################################
# POETRY BASE IMAGE - Provides environment variables for poetry
###############################################################################
FROM duffn/python-poetry:${PYTHON_IMAGE_TAG} AS python-poetry-base

COPY ./poetry.lock ./pyproject.toml ./

# Poetry is installed with `pip` so activate our virtual environment and install projects dependencies
RUN . $VENV_PATH/bin/activate && $POETRY_HOME/poetry install --no-root
EXPOSE 8632
WORKDIR /app
COPY . .

# Our user has an ID of 10000 and the group an ID of 10001.
RUN chown 10000:10001 -R /app

# Our non-root username
USER nonroot

# Use `tini` to start our container
ENTRYPOINT ["tini", "--"]
CMD ["./docker-entrypoint.sh"]
###############################################################################
# POETRY RUNTIME IMAGE - Copies the poetry installation into a smaller image
###############################################################################
# FROM python-poetry-base AS python-poetry
# COPY --from=python-poetry-builder $POETRY_HOME $POETRY_HOME

# ENV FASTAPI_ENV=production

# # Set workdir and copy project files
# WORKDIR /app

# COPY poetry.lock pyproject.toml ./
# RUN poetry config virtualenvs.create false
# RUN poetry install
# COPY gunicorn_conf.py /gunicorn_conf.py
# COPY docker-entrypoint.sh /docker-entrypoint.sh
# RUN chmod +x /docker-entrypoint.sh
# COPY . .

# EXPOSE 3682
# ENTRYPOINT /docker-entrypoint.sh $0 $@
# # CMD ["uvicorn", "--reload", "main:app"]
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app"]