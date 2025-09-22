FROM ubuntu:22.04

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server sudo curl jq openssh-client \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /var/run/sshd

# jump user for all players (MVP); later switch to per-user + SSH keys
RUN useradd -m -s /usr/local/bin/jump-shell jump \
 && echo 'jump:jumppass' | chpasswd

# Script used as the login shell (forced)
COPY jump-shell.sh /usr/local/bin/jump-shell
RUN chmod +x /usr/local/bin/jump-shell \
 && chown root:root /usr/local/bin/jump-shell

# sshd config hardening (no root ssh, allow password for MVP)
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
