FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      openssh-server \
      sudo \
      curl \
 && rm -rf /var/lib/apt/lists/* \
 && mkdir /var/run/sshd

# Create level2 user
RUN useradd -m -s /bin/bash level2 \
 && echo 'level2:level2pass' | chpasswd

# Hidden flag file
COPY flag.txt /home/level2/.secret_flag
RUN chown level2:level2 /home/level2/.secret_flag \
 && chmod 640 /home/level2/.secret_flag

# Add a hint file
RUN echo "Some files are hidden. Try listing all files with the right option." > /home/level2/README.txt \
 && chown level2:level2 /home/level2/README.txt

# Harden SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
 && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
