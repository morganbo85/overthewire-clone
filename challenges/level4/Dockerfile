FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install tools we need
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server sudo curl python3 \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /var/run/sshd

# Create level4 user
RUN useradd -m -s /bin/bash level4 \
 && echo 'level4:level4pass' | chpasswd

# Copy flag and create noisy notes file with exactly one line containing the flag
COPY flag.txt /tmp/flag.txt
COPY make_notes.py /tmp/make_notes.py
RUN python3 /tmp/make_notes.py /home/level4/notes.txt /tmp/flag.txt 200 \
 && chown level4:level4 /home/level4/notes.txt \
 && chmod 644 /home/level4/notes.txt \
 && rm -f /tmp/make_notes.py /tmp/flag.txt

# Hint
RUN echo "This file is noisy. Use grep to find the flag quickly." > /home/level4/README.txt \
 && chown level4:level4 /home/level4/README.txt \
 && chmod 644 /home/level4/README.txt

# Copy entrypoint (regenerates keys and adds submit helper)
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Harden SSH but allow password for MVP
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]