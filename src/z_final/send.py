#!/usr/bin/env python3

import socket
import sys
from time import sleep

from scapy.all import (
    IP,
    UDP,
    Ether,
    FieldLenField,
    IntField,
    IPOption,
    Packet,
    PacketListField,
    ShortField,
    get_if_hwaddr,
    get_if_list,
    sendp
)
from scapy.layers.inet import _IPOption_HDR


def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print("Cannot find eth0 interface")
        exit(1)
    return iface

class SwitchTrace(Packet):
    fields_desc = [ IntField("swid", 0),
                  IntField("qdepth", 0),IntField("ingress_ts", 0),IntField("qtime",0)]
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
                    PacketListField("swtraces",
                                   [],
                                   SwitchTrace,
                                   count_from=lambda pkt:(pkt.count*1)) ]


def main():

    if len(sys.argv)<3:
        print('pass at least the first 2 arguments: <ip> "<message>" (packet_amount) (packet_interval) ')
        exit(1)


    ip = sys.argv[1]
    message = sys.argv[2]
    packet_amount = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    packet_interval = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    print(f"ip={ip} message={message} packet_amount={packet_amount} packet_interval={packet_interval}")

    addr = socket.gethostbyname(ip)
    iface = get_if()

    pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") / IP(
        dst=addr, options = IPOption_MRI(count=0,
            swtraces=[])) / UDP(
            dport=4321, sport=1234) / message
    


 #   pkt = Ether(src=get_if_hwaddr(iface), dst="ff:ff:ff:ff:ff:ff") / IP(
 #       dst=addr, options = IPOption_MRI(count=2,
 #           swtraces=[SwitchTrace(swid=0,qdepth=0), SwitchTrace(swid=1,qdepth=0)])) / UDP(
 #           dport=4321, sport=1234) / sys.argv[2]
    pkt.show2()
    #hexdump(pkt)
    try:
      for i in range(packet_amount):
        sendp(pkt, iface=iface)
        sleep(packet_interval)
    except KeyboardInterrupt:
        raise


if __name__ == '__main__':
    main()
