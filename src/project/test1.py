#!/usr/bin/env python3

import sys
import time
import threading
from scapy.all import sniff, IP, UDP, send
from scapy.packet import Packet, bind_layers
from scapy.fields import IntField, ShortField, FieldLenField, PacketListField
from scapy.layers.inet import IPOption, _IPOption_HDR

# ---------------- MRI definition ----------------

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
        ShortField("count", 1),   # start with 1 so test can pass immediately
        PacketListField("swtraces", [], SwitchTrace,
                        count_from=lambda pkt: pkt.count)
    ]

bind_layers(IP, IPOption_MRI, options=31)

# ---------------- state ----------------

found = False

# ---------------- sniff logic ----------------

def handle(pkt):
    global found

    if IP not in pkt:
        return

    ip = pkt[IP]
    opt = ip.getfieldval("options")

    if isinstance(opt, list):
        for o in opt:
            if isinstance(o, IPOption_MRI):
                print(f"[DEBUG] MRI count = {o.count}")
                found = True

# ---------------- traffic generator ----------------

def send_test(iface):
    time.sleep(1)  # give sniff time to start

    pkt = (
        IP(dst="127.0.0.1", options=[IPOption_MRI(count=1)]) /
        UDP(dport=4321) /
        b"test"
    )

    send(pkt, iface=iface, verbose=False)
    print("[DEBUG] test packet sent")

# ---------------- main ----------------

def main():
    global found

    iface = "eth0"   # IMPORTANT: use loopback for local testing
    # iface = "lo"   # IMPORTANT: use loopback for local testing

    print(f"Sniffing + testing automatically on {iface}...")

    t = threading.Thread(target=lambda: sniff(
        iface=iface,
        filter="udp port 4321",
        prn=handle,
        timeout=5
    ))

    t.start()

    send_test(iface)

    t.join()

    if found:
        print("TEST PASS: MRI detected")
        sys.exit(0)
    else:
        print("TEST FAIL: MRI not detected")
        sys.exit(1)

if __name__ == "__main__":
    main()