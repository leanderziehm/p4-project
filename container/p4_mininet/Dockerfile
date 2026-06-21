# 1. Base Image (Matches config.vm.box)
FROM ubuntu:20.04

# 2. Prevent interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive

# 3. Add system dependencies, build tools, and the p4 user
RUN apt-get update && apt-get install -y \
    sudo \
    wget \
    gnupg \
    ca-certificates \
    build-essential \
    cmake \
    python3-dev \ 
    iputils-ping

RUN useradd -m -s /bin/bash p4 && echo "p4 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/p4

# 4. Copy configuration and patch files (Matches config.vm.provision "file")
# We copy them to the current directory first, then move them if needed
# COPY p4-logo.png p4_16-mode.el p4.vim py3localpath.py clean.sh ./
COPY patches/ ./patches/

# Set permissions (Matches chmod shell commands)
# RUN chmod +755 py3localpath.py clean.sh && chown -R p4:p4 /home/p4

# 5. Run the Bootstrap Scripts (Matches config.vm.provision "shell")
# Note: Docker runs as root by default. Use 'sudo -u p4' for non-privileged scripts.
# COPY root-release-bootstrap.sh root-common-bootstrap.sh user-common-bootstrap.sh ./
COPY root-release-bootstrap.sh user-common-bootstrap.sh ./

RUN ./root-release-bootstrap.sh 
# RUN useradd -m -s /bin/bash p4
COPY patches/ /root/patches/
# COPY p4.vim /root/p4.vim
RUN ./user-common-bootstrap.sh
# RUN echo "p4 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN apt-get install tmux
RUN apt-get install -y mininet
RUN apt-get install -y vim
USER p4
WORKDIR /p4-project
CMD ["/bin/bash"]
# CMD ["bash", "-c", "make && exec bash"]