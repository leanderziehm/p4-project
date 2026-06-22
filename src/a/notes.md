# Notes
## TODO
packet forwarding.
add data to header.
add custom header to packet. 
clone packet.
send cloned packet to other host.

deadline: 
24.06.2026


Context:
Ethernet Packet change destination to next hop mac that matches to destianation ip.

---

32 means match exact ip only one match so same as exact.
    {
      "table": "MyIngress.ipv4_lpm",
      "match": {
        "hdr.ipv4.dstAddr": ["10.0.2.2", 32]
      },
      "action_name": "MyIngress.ipv4_forward",
      "action_params": {
        "dstAddr": "08:00:00:00:01:00",
        "port": 2
      }
    },

<!-- 
In P4, the most common match types are:

Match Type	Example	Description
exact	10.0.2.2	Must match exactly
lpm	10.0.2.0/24	Longest Prefix Match (routing tables)
ternary	value + mask	Arbitrary wildcard matching
range	1000..2000	Match a value within a range
optional	present or wildcard	Match a value or "don't care" (target-dependent) -->

----









node1 node2,latency,bandwidth in Mbit/s,latency
 <!-- ["s1-p3", "s2-p3", "0", 0.5],  -->
```python
   link_dict = {'node1':s,
                        'node2':t,
                        'latency':'0ms',
                        'bandwidth':None
                        }
            if len(link) > 2:
                link_dict['latency'] = self.format_latency(link[2])
            if len(link) > 3:
                link_dict['bandwidth'] = link[3]
```

mininet

dump 
net
nodes



---

        // log_msg(headers.ethernet);
        log_msg("eth {} {} {}",
    {headers.ethernet.dstMac,
     headers.ethernet.srcMac,
     headers.ethernet.etherTypeOrLength});
     bit<48> mac = headers.ethernet.dstMac;

log_msg("MAC {}:{}:{}:{}:{}:{}",
    {
        (bit<8>)((mac >> 40) & 0xFF),
        (bit<8>)((mac >> 32) & 0xFF),
        (bit<8>)((mac >> 24) & 0xFF),
        (bit<8>)((mac >> 16) & 0xFF),
        (bit<8>)((mac >> 8)  & 0xFF),
        (bit<8>)(mac & 0xFF)
    }
);

---

s1-eth1
s1-eth2
Step 2: assign IP to that interface (if needed)

Example:

sudo ip addr add 10.0.0.254/24 dev s1-eth1
Step 3: add route to Mininet subnet
sudo ip route add 10.0.0.0/8 dev s1-eth1

Now:

ping 10.0.1.1