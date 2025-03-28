#!/bin/bash
set -eo pipefail
shopt -s nullglob

exec uvicorn app.main:app --host ${HOST} --port ${PORT}
