#!/usr/bin/env python3
import json
from datetime import datetime

from scapy.all import (
    UDP,
    Raw
)    # IP,
from scapy.layers.inet import IP
from scapy.packet import Packet
from scapy.utils import ltoa

LOG_FILE = "packets.log"

def extract_packet_info(pkt:Packet):

    entry = {
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        if IP in pkt:
            entry["src_ip"] = pkt[IP].src
            entry["dst_ip"] = pkt[IP].dst
            pkt_ip = pkt[IP]

            dscp = pkt_ip.tos >> 2
            ecn = pkt_ip.tos & 0x03
            data = {
                "version": pkt_ip.version,
                "ihl": pkt_ip.ihl,
                "tos": pkt_ip.tos,
                "dscp" : dscp,
                "ecn": ecn,
                "len": pkt_ip.len,
                "id": pkt_ip.id,
                "ttl": pkt_ip.ttl,
                "proto": pkt_ip.proto,
                }
            
            entry.update(data)

        if UDP in pkt:
            entry["src_port"] = pkt[UDP].sport
            entry["dst_port"] = pkt[UDP].dport

        if Raw in pkt:
            payload = pkt[Raw].load.decode(errors="ignore")
            entry["payload"] = payload

        switches = []

        if IP in pkt and pkt[IP].options:

            # print("hi")
            # print(pkt[IP].options)
            

            for option in pkt[IP].options:

                if hasattr(option, "originalDstAddr"):
                    # print("originalDstAddr")
                    # print(option.originalDstAddr)
                    # ip_string = option.originalDstAddr
                    ip_string = ltoa(option.originalDstAddr)
                    # print(ip_string)
                    entry["originalDstAddr"] = ip_string



                if hasattr(option, "swtraces"):
                    last_ingess = None
                    for trace in option.swtraces:
                        delta = None
                        if last_ingess is not None:
                            # print("last_ingess",last_ingess)
                            delta = trace.ingress_ts - last_ingess
                            # print("delta:",delta)

                            # first one is always 0.
                            # last one doenst have something to compare to.
                        
                        last_ingess = trace.ingress_ts

                        switch_data= {
                            "swid": trace.swid,
                            "qdepth": trace.qdepth,
                            "ingress_ts": trace.ingress_ts,
                            "qtime": trace.qtime,  
                        }
                        
                        if delta  is not None:
                            switch_data["hop_ts_delta"]= delta

                        switches.append(switch_data)
                        

        entry["switches"] = switches
        entry["hop_count"] = len(switches)

    except Exception as e:
        entry["error"] = str(e)

    return entry


def log_packet(pkt:Packet):

    entry = extract_packet_info(pkt)

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

