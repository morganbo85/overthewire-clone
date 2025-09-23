#!/usr/bin/env bash
set -euo pipefail

# Regenerate SSH host keys on start
rm -f /etc/ssh/ssh_host_*
ssh-keygen -A

# Create submit_flag helper that uses internal backend service (backend:8000)
BACKEND_HOST="${BACKEND_HOST:-backend:8000}"

cat >/usr/local/bin/submit_flag <<'EOF'
#!/usr/bin/env bash
if [ -z "$1" ]; then
  echo "Usage: submit_flag FLAG"
  exit 1
fi
FLAG="$1"
curl -s -X POST "http://${BACKEND_HOST}/submit" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"bo\",\"password\":\"testpass\",\"flag\":\"${FLAG}\"}"
EOF
chmod +x /usr/local/bin/submit_flag

# ensure home permissions
chown -R level3:level3 /home/level3

exec /usr/sbin/sshd -D
