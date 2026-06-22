
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