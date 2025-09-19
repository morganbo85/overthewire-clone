#!/usr/bin/env bash
set -euo pipefail

# Regenerate SSH host keys (remove existing and generate fresh)
rm -f /etc/ssh/ssh_host_*
ssh-keygen -A

# Create a small helper for users to submit flags from inside the container
# It uses environment BACKEND_HOST (default to docker-compose service 'backend' name).
BACKEND_HOST="${BACKEND_HOST:-backend:8000}"
cat >/usr/local/bin/submit_flag <<'EOF'
#!/usr/bin/env bash
if [ -z "$1" ]; then
  echo "Usage: submit_flag FLAG"
  exit 1
fi
FLAG="$1"
# Note: this uses a hardcoded username/password for the challenge demo.
curl -s -X POST "http://${BACKEND_HOST}/submit" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"bo\",\"password\":\"testpass\",\"level\":\"level1\",\"flag\":\"${FLAG}\"}"
EOF
chmod +x /usr/local/bin/submit_flag

# Ensure proper permissions for /home/level1
chown -R level1:level1 /home/level1

# Start sshd in foreground
exec /usr/sbin/sshd -D
