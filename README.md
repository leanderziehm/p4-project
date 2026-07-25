# README.md

## In Network Telemetry

The environment is containerized using Podman/Docker to simplify setup and ensure reproducibility.

# A. if want to test with podman ouside of virtual machine

1. run podman with:
```
make main
```
or 
```
cd container/p4_mininet && make
```
then follow B:

# B:

##  1. Step
```
make 1
```
or

```
cd main_code && make build && make run
```
in mininet
```
xterm h1 h2 h3
```

in h3 (which is the telemetry sink):
```
python3 ./telemetry_receive.py
```
in h2 terminal:
```
./receive.py
```
then

in h1 terminal:
```
./send.py 10.0.2.2 "P4 is cool" 30
```
or for auto send to random host on network with random text:
```
python3 experiment.py
```

##  2. Step

make sure you have installed elasticsearch:
```
python3 -m pip install "elasticsearch>=8,<9"
```


either connect over ssh port tunnel to our server or selfhost the container of elasticsearch at 9200 then
open another terminal tab or in tmux
go to mri_clone or z_final 
```
make ssh
```
```
cd src/z_final && python3 background_log_to_elastic.py
```

then you can see your data in kibana at port 5601 http://localhost:5601/
