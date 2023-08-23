#!/bin/sh

set -e

# activate the virtual environment created by Poetry
. /venv/bin/activate

# run the command passed to the entrypoint
exec gunicorn -k uvicorn.workers.UvicornWorker -c ./gunicorn_conf.py app.main:app