#!/usr/bin/env python3
import sys

from scapy.all import (
    ByteField,
    FieldLenField,
    IntField,
    IPOption,
    Packet,
    PacketListField,
    ShortField,
    ThreeBytesField,
    get_if_list,
    sniff
)
from scapy.layers.inet import _IPOption_HDR
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


# def log_packet(pkt:Packet):

#     entry = extract_packet_info(pkt)

#     with open(LOG_FILE, "a") as f:
#         f.write(json.dumps(entry) + "\n")




def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class SwitchTrace(Packet):
    # Must match switch_t in mri.p4: swid8 + qdepth24 + ingress_ts32 + qtime32 = 12 bytes.
    fields_desc = [
        ByteField("swid", 0),
        ThreeBytesField("qdepth", 0),
        IntField("ingress_ts", 0),
        IntField("qtime", 0),
    ]
    
    def extract_padding(self, p):
                return "", p

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [ _IPOption_HDR,
                    FieldLenField("length", None, fmt="B",
                                  length_of="swtraces",
                                  adjust=lambda pkt,l:l*2+4),
                    ShortField("count", 0),
                    IntField("originalDstAddr", 0),
                    PacketListField("swtraces",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]

def handle_pkt(pkt):
    print("got a packet")
    pkt.show2()

    entry = extract_packet_info(pkt)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")
        
#    hexdump(pkt)
    sys.stdout.flush()


def main():
    iface = 'eth0'
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="(udp or tcp)", iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
