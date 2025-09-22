#!/usr/bin/env bash
set -euo pipefail

# This script runs when the 'jump' user logs in.
# It asks the backend which level the supplied username should reach
# then proxies the SSH session to that level container (hostnames are service names).

BACKEND_HOST="${BACKEND_HOST:-backend:8000}"

# Prompt for a game username (MVP). Later: map SSH username -> game username or use SSH keys.
echo -n "Enter your game username: "
read -r GAMEUSER

# Query backend for current_level
LEVEL=$(curl -s "http://${BACKEND_HOST}/progress?username=${GAMEUSER}" | jq -r '.current_level' || echo "")

if [[ -z "${LEVEL}" || "${LEVEL}" == "null" ]]; then
  echo "Could not determine your level. Check your username or try again."
  exit 1
fi

TARGET="level${LEVEL}"
echo "Routing ${GAMEUSER} to ${TARGET} ..."
# StrictHostKeyChecking=no to avoid interactive prompt inside the bastion
exec ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "${TARGET}" -l "${TARGET}" -t
