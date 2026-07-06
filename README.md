# README.md

## In Network Telemetry

The environment is containerized using Podman/Docker to simplify setup and ensure reproducibility.



# in virtual machine:

##  1. Step
```
make
```
or

```
cd src/mri_clone && make build && make run
```
in mininet
```
xterm h1 h2 h3
```

in h2 and h3 terminal:
```
./receive.py
```
then

in h1 terminal:
```
./send.py 10.0.2.2 "P4 is cool" 30
```

##  2. Step

install elasticsearch:
```
python3 -m pip install "elasticsearch>=8,<9"
```

either connect over ssh port tunnel to our server or selfhost the container of elasticsearch at 9200 then
open another terminal tab or in tmux
go to mri_clone or z_final 
```
python3 background_log_to_elastic.py
```

then you can see your data in kibana at port 5601



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



# Features in split vs mri_clone

ecn if conjested.
cloning with multi switch final hop.


# need to check 
does mri header get removed before arriving?
does ecn ever get set? (with log check)




h1 iperf

does debug header work?


# TODO 

before sumbit figur out why text is trunkated when setting mri and switchtraches to invalid.


kibana dashboard.
figure out why its cut off in h2.
Biggest goal make demo work. new topology. Different topology to make it work for real.
consjestion and delay and send experiment. 
add data for tracking.