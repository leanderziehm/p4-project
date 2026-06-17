#!/usr/bin/env python3

import sys
import json
from datetime import datetime

from scapy.all import (
    FieldLenField,
    IntField,
    IPOption,
    Packet,
    PacketListField,
    ShortField,
    get_if_list,
    sniff,
    IP,
    UDP,
    Raw
)

from scapy.layers.inet import _IPOption_HDR


LOG_FILE = "packets.log"


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


class SwitchTrace(Packet):
    fields_desc = [
        IntField("swid", 0),
        IntField("qdepth", 0),
        IntField("ingress_ts", 0),
        IntField("qtime", 0)
    ]

    def extract_padding(self, p):
        return "", p


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


def extract_packet_info(pkt):

    entry = {
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        if IP in pkt:
            entry["src_ip"] = pkt[IP].src
            entry["dst_ip"] = pkt[IP].dst

        if UDP in pkt:
            entry["src_port"] = pkt[UDP].sport
            entry["dst_port"] = pkt[UDP].dport

        if Raw in pkt:
            payload = pkt[Raw].load.decode(errors="ignore")
            entry["payload"] = payload

        switches = []

        if IP in pkt and pkt[IP].options:

            for option in pkt[IP].options:

                if hasattr(option, "swtraces"):

                    for trace in option.swtraces:

                        switches.append({
                            "swid": trace.swid,
                            "qdepth": trace.qdepth,
                            "ingress_ts": trace.ingress_ts,
                            "qtime": trace.qtime
                        })

        entry["switches"] = switches
        entry["hop_count"] = len(switches)

    except Exception as e:
        entry["error"] = str(e)

    return entry


def log_packet(pkt):

    entry = extract_packet_info(pkt)

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def handle_pkt(pkt):

    print("Received packet")

    log_packet(pkt)

    sys.stdout.flush()


def main():

    iface = get_if()

    print(f"Logging packets to {LOG_FILE}")
    print(f"Sniffing on {iface}")

    sys.stdout.flush()

    sniff(
        iface=iface,
        filter="udp and port 4321",
        prn=handle_pkt
    )


if __name__ == "__main__":
    main()