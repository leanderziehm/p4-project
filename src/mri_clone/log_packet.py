#!/usr/bin/env python3
import json
from datetime import datetime

from scapy.all import (
    UDP,
    Raw
)    # IP,
from scapy.layers.inet import IP
from scapy.packet import Packet


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


def log_packet(pkt:Packet):

    entry = extract_packet_info(pkt)

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

