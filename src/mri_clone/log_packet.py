#!/usr/bin/env python3
import json
from datetime import datetime

from scapy.all import (
    IP,
    UDP,
    Raw
)

LOG_FILE = "packets.log"


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
                            # "ingress_ts": trace.ingress_ts,
                            # "qtime": trace.qtime,
                            # "pkt_len": trace.pkt_len
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

