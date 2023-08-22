#!/bin/sh

set -e

# activate the virtual environment created by Poetry
. /opt/poetry/cache/virtualenvs

# run the command passed to the entrypoint
exec "$@"