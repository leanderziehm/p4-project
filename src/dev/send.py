#!/usr/bin/env python3
# send.py

import socket
import sys
from time import sleep

from scapy.all import (
    Ether,
    FieldLenField,
    IntField,
    IP,
    IPOption,
    Packet,
    PacketListField,
    ShortField,
    UDP,
    get_if_hwaddr,
    get_if_list,
    sendp
)

from scapy.layers.inet import _IPOption_HDR


# -----------------------------
# Interface selection
# -----------------------------
def get_if():
    iface = None

    for i in get_if_list():
        if "eth0" in i:
            iface = i
            break

    if iface is None:
        print("Cannot find eth0 interface")
        sys.exit(1)

    return iface


# -----------------------------
# Custom switch telemetry header
# -----------------------------
class SwitchTrace(Packet):
    fields_desc = [
        IntField("swid", 0),
        IntField("qdepth", 0),
        IntField("ingress_ts", 0),
        IntField("qtime", 0),
        IntField("pkt_len", 0)
    ]

    def extract_padding(self, p):
        return "", p


# -----------------------------
# MRI IP option
# -----------------------------
class IPOption_MRI(IPOption):
    name = "MRI"
    option = 31

    fields_desc = [
        _IPOption_HDR,

        FieldLenField(
            "length",
            None,
            fmt="B",
            length_of="swtraces",
            adjust=lambda pkt, l: l * 2 + 4
        ),

        ShortField("count", 0),

        PacketListField(
            "swtraces",
            [],
            SwitchTrace,
            count_from=lambda pkt: pkt.count
        )
    ]


# -----------------------------
# Main sender
# -----------------------------
def main():

    if len(sys.argv) < 6:
        print(
            "Usage:\n"
            "python3 send.py <dst_host> <experiment_id> "
            "<count> <interval_sec> <message...>"
        )
        sys.exit(1)

    dst_host = sys.argv[1]
    experiment_id = sys.argv[2]
    count = int(sys.argv[3])
    interval = float(sys.argv[4])

    # IMPORTANT FIX:
    # allow full multi-word / paragraph payloads
    message = " ".join(sys.argv[5:]).strip()

    iface = get_if()

    addr = socket.gethostbyname(dst_host)

    print(f"Destination : {addr}")
    print(f"Experiment  : {experiment_id}")
    print(f"Count       : {count}")
    print(f"Interval    : {interval}")
    print(f"Payload size: {len(message)} chars")

    try:
        for seq in range(count):

            payload = f"{experiment_id},{seq},{message}"

            pkt = (
                Ether(
                    src=get_if_hwaddr(iface),
                    dst="ff:ff:ff:ff:ff:ff"
                )
                /
                IP(
                    dst=addr,
                    options=IPOption_MRI(
                        count=0,
                        swtraces=[]
                    )
                )
                /
                UDP(
                    sport=1234,
                    dport=4321
                )
                /
                payload
            )

            sendp(pkt, iface=iface, verbose=False)

            sleep(interval)

        print("Finished sending.")

    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()