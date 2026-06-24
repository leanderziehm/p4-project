#!/usr/bin/env python3
import socket
import struct
import threading
import time
import os

# ---------- interface index mapping ----------

def get_ifname_map():
    ifnames = {}
    for iface in os.listdir('/sys/class/net/'):
        try:
            idx = socket.if_nametoindex(iface)
            ifnames[idx] = iface
        except:
            pass
    return ifnames


# ---------- global stats ----------

stats = {}
lock = threading.Lock()


# ---------- sniff ALL interfaces ----------

def sniffer():
    # AF_PACKET raw socket
    s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))

    ifmap = get_ifname_map()

    while True:
        pkt, ancdata, flags, addr = s.recvmsg(65535, 1024)

        if_index = addr[2]
        iface = ifmap.get(if_index, str(if_index))

        with lock:
            if iface not in stats:
                stats[iface] = 0
            stats[iface] += 1


# ---------- compute rates ----------

def rate_loop():
    prev = {}

    while True:
        time.sleep(1)

        with lock:
            snapshot = dict(stats)

        print("\n--- packets/sec ---")

        for iface, count in snapshot.items():
            prev_count = prev.get(iface, 0)
            rate = count - prev_count
            prev[iface] = count

            print(f"{iface}: {rate}")


# ---------- main ----------

if __name__ == "__main__":
    print("Starting global sniffer (all interfaces)...")

    t = threading.Thread(target=sniffer, daemon=True)
    t.start()

    rate_loop()