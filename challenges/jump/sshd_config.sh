mkdir -p /home/jump/.ssh
cat > /home/jump/.ssh/config <<EOF
Host level1
    HostName level1
    User level1
    Port 22
EOF
chown -R jump:jump /home/jump/.ssh
chmod 600 /home/jump/.ssh/config
