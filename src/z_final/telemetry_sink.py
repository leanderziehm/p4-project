#!/usr/bin/env python3

import argparse
import queue
import threading
from datetime import datetime

from elasticsearch import Elasticsearch
from scapy.all import sniff, UDP, Raw
from scapy.layers.inet import IP
from scapy.packet import Packet
from scapy.utils import ltoa

INDEX = "mri-packets"
ES_HOST = "http://localhost:9200"

es = Elasticsearch(ES_HOST)

packet_queue = queue.Queue(maxsize=5000)


def extract_packet_info(pkt: Packet):
    entry = {
        "timestamp": datetime.utcnow().isoformat()
    }

    try:
        if IP in pkt:
            ip = pkt[IP]

            entry.update({
                "src_ip": ip.src,
                "dst_ip": ip.dst,
                "version": ip.version,
                "ihl": ip.ihl,
                "tos": ip.tos,
                "dscp": ip.tos >> 2,
                "ecn": ip.tos & 0x03,
                "len": ip.len,
                "id": ip.id,
                "ttl": ip.ttl,
                "proto": ip.proto,
            })

        if UDP in pkt:
            entry["src_port"] = pkt[UDP].sport
            entry["dst_port"] = pkt[UDP].dport

        if Raw in pkt:
            entry["payload"] = pkt[Raw].load.decode(errors="ignore")

        switches = []

        if IP in pkt and pkt[IP].options:
            for option in pkt[IP].options:

                if hasattr(option, "originalDstAddr"):
                    entry["originalDstAddr"] = ltoa(option.originalDstAddr)

                if hasattr(option, "swtraces"):
                    last_ingress = None

                    for trace in option.swtraces:

                        sw = {
                            "swid": trace.swid,
                            "qdepth": trace.qdepth,
                            "ingress_ts": trace.ingress_ts,
                            "qtime": trace.qtime,
                        }

                        if last_ingress is not None:
                            sw["hop_ts_delta"] = (
                                trace.ingress_ts - last_ingress
                            )

                        last_ingress = trace.ingress_ts
                        switches.append(sw)

        entry["switches"] = switches
        entry["hop_count"] = len(switches)

    except Exception as e:
        entry["error"] = str(e)

    return entry


def elastic_worker():
    while True:
        doc = packet_queue.get()

        try:
            es.index(index=INDEX, document=doc)
        except Exception as e:
            print("Elastic error:", e)

        packet_queue.task_done()


def packet_handler(pkt):
    try:
        packet_queue.put_nowait(extract_packet_info(pkt))
    except queue.Full:
        print("Queue full, dropping packet")


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-i",
        "--iface",
        default=None,
        help="Interface to sniff"
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=4321,
        help="UDP port"
    )

    args = parser.parse_args()

    threading.Thread(
        target=elastic_worker,
        daemon=True
    ).start()

    print(f"Listening on UDP port {args.port}")

    sniff(
        iface=args.iface,
        filter=f"udp port {args.port}",
        prn=packet_handler,
        store=False,
    )


if __name__ == "__main__":
    main()