#!/usr/bin/env bash
# wait-for-it.sh: Wait until a host:port are available
# Usage: wait-for-it.sh host:port -- command args

set -e

hostport=$1
shift

host=$(echo $hostport | cut -d: -f1)
port=$(echo $hostport | cut -d: -f2)

while ! nc -z $host $port; do
  echo "Waiting for $host:$port..."
  sleep 1
done

exec "$@"
