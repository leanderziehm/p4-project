AUTOMATE THIS: 

make
then

You should now see a Mininet command prompt. Open four terminals
for h1, h11, h2, h22, respectively:
mininet> xterm h1 h11 h2 h22


In h2's xterm, start the server that captures packets:
./receive.py


in h22's xterm, start the iperf UDP server:
iperf -s -u


In h1's xterm, send one packet per second to h2 using send.py
say for 30 seconds:
./send.py 10.0.2.2 "P4 is cool" 30
The message "P4 is cool" should be received in h2's xterm,


In h11's xterm, start iperf client sending for 15 seconds
iperf -c 10.0.2.22 -t 15 -u


At h2, the MRI header has no hop info (count=0)


type exit to close each xterm window