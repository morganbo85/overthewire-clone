FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install tools
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server sudo curl xxd \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /var/run/sshd

# Create level5 user
RUN useradd -m -s /bin/bash level5 \
 && echo 'level5:level5pass' | chpasswd

# Create a binary-like file that contains the flag string inside random bytes
COPY flag.txt /tmp/flag.txt
RUN dd if=/dev/urandom bs=1 count=2048 of=/home/level5/mystery.bin 2>/dev/null \
 && printf '\n' >> /home/level5/mystery.bin \
 && cat /tmp/flag.txt >> /home/level5/mystery.bin \
 && dd if=/dev/urandom bs=1 count=1024 >> /home/level5/mystery.bin 2>/dev/null \
 && chown level5:level5 /home/level5/mystery.bin \
 && chmod 644 /home/level5/mystery.bin \
 && rm -f /tmp/flag.txt

# Add hint
RUN echo "Some useful text can hide inside binaries. Try the 'strings' command." > /home/level5/README.txt \
 && chown level5:level5 /home/level5/README.txt \
 && chmod 644 /home/level5/README.txt

# Copy entrypoint (regenerate ssh host keys + submit helper)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Harden SSH (allow password auth for MVP)
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
