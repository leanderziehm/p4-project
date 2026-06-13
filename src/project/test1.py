#!/usr/bin/env python3

import sys
from scapy.all import sniff, IP, UDP
from scapy.layers.inet import IPOption
from scapy.packet import bind_layers

# Import your shared definitions (recommended to move them into a common module)
from scapy.all import Packet, IntField, ShortField, FieldLenField, PacketListField
from scapy.layers.inet import _IPOption_HDR

class SwitchTrace(Packet):
    fields_desc = [
        IntField("swid", 0),
        IntField("qdepth", 0)
    ]

class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31
    fields_desc = [
        _IPOption_HDR,
        FieldLenField("length", None, fmt="B",
                      length_of="swtraces",
                      adjust=lambda pkt, l: l * 2 + 4),
        ShortField("count", 0),
        PacketListField("swtraces", [], SwitchTrace,
                        count_from=lambda pkt: pkt.count)
    ]

# Force Scapy to decode option 31 as MRI
bind_layers(IP, IPOption_MRI, options=31)

found = False

def handle(pkt):
    global found

    if IP not in pkt:
        return

    ip = pkt[IP]

    opt = ip.getfieldval("options")

    # Extract MRI option safely
    if isinstance(opt, list):
        for o in opt:
            if isinstance(o, IPOption_MRI):
                print(f"[DEBUG] MRI count = {o.count}")
                print(f"[DEBUG] switch traces = {len(o.swtraces)}")

                if o.count > 0:
                    found = True

def main():
    iface = "h2-eth0"
    print(f"Sniffing on {iface} for MRI packets...")

    sniff(
        iface=iface,
        filter="udp and port 4321",
        prn=handle,
        timeout=10
    )

    if found:
        print("TEST PASS: MRI count > 0 detected")
        sys.exit(0)
    else:
        print("TEST FAIL: No MRI count > 0 detected")
        sys.exit(1)

if __name__ == "__main__":
    main()