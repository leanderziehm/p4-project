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
from log_packet import log_packet # +

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

    log_packet(pkt)
        
#    hexdump(pkt)
    sys.stdout.flush()


def main():
    iface = 'eth0'
    print("sniffing on %s" % iface)
    sys.stdout.flush()
    sniff(filter="(udp or tcp) and port 1234", iface = iface,
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
