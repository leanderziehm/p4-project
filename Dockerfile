FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    mininet \
    openvswitch-switch \
    iproute2 \
    iputils-ping \
    net-tools \
    curl \
    git \
    python3 \
    python3-pip

# clone p4c
RUN git clone --depth 1 --single-branch --filter=blob:none https://github.com/p4lang/p4c.git /p4c

CMD service openvswitch-switch start && bash