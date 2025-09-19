FROM ubuntu:22.04

RUN apt-get update && apt-get install -y openssh-server ssh sudo \
    && mkdir /var/run/sshd

# Create a jump user
RUN useradd -m -s /bin/bash jump \
    && echo 'jump:jumppass' | chpasswd

# Force the jump user to always proxy into level1
RUN echo 'command="ssh -o StrictHostKeyChecking=no level1" jump' >> /home/jump/.ssh/authorized_keys || true

# Harden SSH
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config \
    && sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]

COPY sshd_config.sh /sshd_config.sh
RUN bash /sshd_config.sh
