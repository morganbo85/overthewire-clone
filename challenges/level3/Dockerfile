FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install base tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server sudo curl jq \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /var/run/sshd

# Create level3 user
RUN useradd -m -s /bin/bash level3 \
 && echo 'level3:level3pass' | chpasswd

# Add files:
# - a protected flag owned by root and unreadable by level3
# - a readable file containing the real useful flag (lesson: permissions matter)
COPY flag.txt /root/protected_flag.txt
RUN chown root:root /root/protected_flag.txt \
 && chmod 600 /root/protected_flag.txt

# Place the playable flag somewhere readable (the 'right' place they should find)
RUN echo "FLAG{this_is_level3}" > /home/level3/available_flag.txt \
 && chown level3:level3 /home/level3/available_flag.txt \
 && chmod 640 /home/level3/available_flag.txt

# Hint file to nudge players to check permissions and alternative files
RUN echo "Some files are protected by root permissions (you may not be able to read them). Try looking for other files you *can* read in this directory." > /home/level3/README.txt \
 && chown level3:level3 /home/level3/README.txt \
 && chmod 644 /home/level3/README.txt

# Copy entrypoint that regenerates SSH host keys and creates submit helper
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Harden SSH (allow password auth for MVP)
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
