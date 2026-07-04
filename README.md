# README.md

## In Network Telemetry

The environment is containerized using Podman/Docker to simplify setup and ensure reproducibility.



# in virtual machine:

```
make
```

in mininet
```
xterm h1 h2 h3
```

in h1 terminal:
```
./send.py 10.0.2.2 "P4 is cool" 30
```
in h2 and h3 terminal:
```
./receive.py
```



# if want to test with podman ouside of virtual machine

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