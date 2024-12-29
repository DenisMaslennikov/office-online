#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

readonly cmd="$*"

: "${DATABASE_HOST:=db}"
: "${DATABASE_PORT:=5432}"
: "${RABBITMQ_HOST:=rabbitmq}"
: "${RABBITMQ_PORT:=5672}"

# We need this line to make sure that this container is started
# after the one with postgres:
/wait-for-it.sh \
  --host="$DATABASE_HOST" \
  --port="$DATABASE_PORT" \
  --timeout=90 \
  --strict

# It is also possible to wait for other services as well: redis, elastic, mongo
echo "Postgres ${DATABASE_HOST}:${DATABASE_PORT} is up"

/wait-for-it.sh \
  --host="$RABBITMQ_HOST" \
  --port="$RABBITMQ_PORT" \
  --timeout=90 \
  --strict

echo "Rabbitmq ${RABBITMQ_HOST}:${RABBITMQ_PORT} is up"

# Evaluating passed command (do not touch):
# shellcheck disable=SC2086
exec $cmd
