# Start with the official P4 compiler image
FROM docker.io/p4lang/p4c:latest

# Set non-interactive for apt installations
ENV DEBIAN_FRONTEND=noninteractive

# Update and install networking tools needed for Mininet/OVS
# Note: p4lang/p4c is Debian-based, so apt-get works here too.
RUN apt-get update && apt-get install -y \
    mininet \
    openvswitch-switch \
    iproute2 \
    iputils-ping \
    net-tools \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create target directory
WORKDIR /p4-project/src
# Start OVS service and drop into bash
# Note: Running Mininet inside Docker usually requires --privileged mode
CMD service openvswitch-switch start && /bin/bash