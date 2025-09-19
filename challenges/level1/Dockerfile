FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server sudo curl \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /var/run/sshd

# Create a user for the challenge
RUN useradd -m -s /bin/bash level1 \
 && echo 'level1:level1pass' | chpasswd

# Add the flag
COPY flag.txt /home/level1/flag.txt
RUN chown level1:level1 /home/level1/flag.txt \
 && chmod 640 /home/level1/flag.txt

# Copy entrypoint that regenerates host keys on start
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Harden SSH config: disable root login (keep password auth for ease of play)
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
