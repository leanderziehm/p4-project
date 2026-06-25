# README.md

## In Network Telemetry

The environment is containerized using Podman/Docker to simplify setup and ensure reproducibility.

1. run podman with:
```
make main
```

2. in container:
```
make
```

3. in mininet
```
h1 ping -i 0.01 h2
```