#!/usr/bin/env python3
"""
Automated test for Multi-Hop Route Inspection (MRI).

Validates that packets received at h2 contain MRI headers with count != 0,
meaning at least one switch hop was recorded.

Usage (run from the exercise directory, with Mininet already up via `make`):
    sudo python3 test_mri.py

Or to also launch Mininet automatically:
    sudo python3 test_mri.py --launch
"""

import argparse
import subprocess
import sys
import time
import threading
import os
import signal
from scapy.all import (
    sniff, Ether, IP, UDP, Raw,
    BitField, ByteField, ShortField, XByteField,
    Packet, bind_layers, IPOption
)

# ---------------------------------------------------------------------------
# Scapy header definitions (must match mri.p4)
# ---------------------------------------------------------------------------

class SwitchTrace(Packet):
    """One hop entry: switch ID + queue depth."""
    name = "SwitchTrace"
    fields_desc = [
        BitField("swid",   0, 32),
        BitField("qdepth", 0, 32),
    ]

    def guess_payload_class(self, payload):
        # Chain additional SwitchTrace entries if payload is long enough
        return SwitchTrace if len(payload) >= 8 else Packet


class MRI(IPOption):
    """IP Option type 31 carrying MRI data."""
    name = "MRI"
    option = 31
    fields_desc = [
        XByteField("copy_flag", 0x00),   # copy_flag + optclass packed into one byte
        XByteField("option",    31),
        ByteField("length",     4),
        ShortField("count",     0),
    ]

    def extract_padding(self, s):
        return b"", s


# Bind MRI option so Scapy parses it inside IP options automatically
bind_layers(IP,  MRI,  proto=0x11)   # broad bind; real parsing is via option field


# ---------------------------------------------------------------------------
# Test configuration
# ---------------------------------------------------------------------------

RECEIVE_IFACE  = "h2-eth0"          # interface to sniff on inside Mininet network ns
SEND_HOST      = "10.0.2.2"         # h2's IP
SEND_PORT_DST  = 4321
SEND_PORT_SRC  = 1234
IPERF_TARGET   = "10.0.2.22"        # h22's IP
IPERF_DURATION = 15                 # seconds
PACKET_COUNT   = 5                  # how many MRI-tagged packets to send
WAIT_SECONDS   = 20                 # total capture window
MRI_OPTION     = 31                 # option type for MRI
PASS_THRESHOLD = 1                  # at least this many packets must have count > 0


# ---------------------------------------------------------------------------
# Packet capture
# ---------------------------------------------------------------------------

captured_results = []   # list of (count, [swid, ...]) tuples


def parse_mri_packet(pkt):
    """
    Return (count, swids) extracted from a packet's IP options,
    or None if no MRI option is found.
    """
    if IP not in pkt:
        return None

    raw_opts = bytes(pkt[IP].options) if pkt[IP].options else b""
    # Walk raw IP options looking for type 31
    i = 0
    while i < len(raw_opts):
        opt_type = raw_opts[i]
        if opt_type == 0:          # end-of-options pad
            break
        if opt_type == 1:          # NOP
            i += 1
            continue
        if i + 1 >= len(raw_opts):
            break
        opt_len = raw_opts[i + 1]
        if opt_type == MRI_OPTION and opt_len >= 4:
            # Bytes: [type][len][count_hi][count_lo][swid×4 qdepth×4 ...]
            count = int.from_bytes(raw_opts[i+2:i+4], "big")
            swids = []
            offset = i + 4
            for _ in range(count):
                if offset + 8 > len(raw_opts):
                    break
                swid   = int.from_bytes(raw_opts[offset:offset+4], "big")
                qdepth = int.from_bytes(raw_opts[offset+4:offset+8], "big")
                swids.append((swid, qdepth))
                offset += 8
            return count, swids
        i += opt_len if opt_len > 0 else 1
    return None


def packet_handler(pkt):
    """Callback for each sniffed packet."""
    result = parse_mri_packet(pkt)
    if result is not None:
        count, swids = result
        captured_results.append((count, swids))
        status = "PASS" if count > 0 else "FAIL (count=0)"
        print(f"  [CAPTURED] count={count}  swids={swids}  → {status}")


def start_sniffer(iface, timeout):
    """Start Scapy sniff in a background thread."""
    def _sniff():
        sniff(
            iface=iface,
            filter="udp dst port 4321",
            prn=packet_handler,
            timeout=timeout,
            store=False,
        )
    t = threading.Thread(target=_sniff, daemon=True)
    t.start()
    return t


# ---------------------------------------------------------------------------
# Traffic generation (used when NOT launching Mininet automatically)
# ---------------------------------------------------------------------------

def send_mri_packets(dst_ip, count):
    """
    Send UDP packets with IP option type 31 set (minimal MRI header, count=0).
    The switches will fill in the hop info.
    """
    from scapy.all import send as scapy_send

    # Build a minimal MRI option: type=31, len=4, count=0
    opt_bytes = bytes([MRI_OPTION, 4, 0, 0])
    # Pad to 4-byte boundary (already 4 bytes, but IP options must pad to multiple of 4)
    raw_opt = opt_bytes

    pkt = (
        Ether()
        / IP(dst=dst_ip, options=raw_opt)
        / UDP(sport=SEND_PORT_SRC, dport=SEND_PORT_DST)
        / Raw(load=b"MRI test packet")
    )

    print(f"  Sending {count} UDP packet(s) to {dst_ip}:{SEND_PORT_DST} ...")
    for i in range(count):
        scapy_send(pkt, verbose=False)
        time.sleep(1)


# ---------------------------------------------------------------------------
# Mininet-integrated mode (--launch flag)
# ---------------------------------------------------------------------------

def run_in_mininet():
    """
    Drive traffic through the existing Mininet topology using subprocess calls
    to `mn` CLI (assumes `make` has already been run and Mininet is up, OR
    that this script is run via `mn --custom ...`).

    For simplicity this uses subprocess to exec commands in the host namespaces.
    """
    print("[*] Running traffic via Mininet host namespaces ...")

    def mn_cmd(host, cmd, bg=False):
        """Run a command in a Mininet host's network namespace."""
        # Mininet stores host PIDs; we use `ip netns exec` equivalent via mnexec
        full = f"mnexec -a {host} {cmd}"
        if bg:
            return subprocess.Popen(full, shell=True,
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        return subprocess.run(full, shell=True, capture_output=True, text=True)

    # Start iperf server on h22
    iperf_server = mn_cmd("h22", "iperf -s -u", bg=True)
    time.sleep(0.5)

    # Start iperf client on h11 (background, 15s)
    iperf_client = mn_cmd(
        "h11",
        f"iperf -c {IPERF_TARGET} -t {IPERF_DURATION} -u",
        bg=True
    )

    # Send low-rate packets from h1 using send.py
    sender = mn_cmd(
        "h1",
        f"./send.py {SEND_HOST} 'MRI test' {PACKET_COUNT}",
        bg=True
    )

    return iperf_server, iperf_client, sender


# ---------------------------------------------------------------------------
# Result evaluation
# ---------------------------------------------------------------------------

def evaluate_results():
    """Print summary and return True if test passes."""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total MRI packets captured : {len(captured_results)}")

    passing = [r for r in captured_results if r[0] > 0]
    failing = [r for r in captured_results if r[0] == 0]

    print(f"Packets with count  > 0    : {len(passing)}  ✓")
    print(f"Packets with count == 0    : {len(failing)}  ✗")

    if len(captured_results) == 0:
        print("\n[FAIL] No MRI packets were captured.")
        print("       Check that mri.p4 is compiled and Mininet is running.")
        return False

    if len(passing) >= PASS_THRESHOLD:
        print(f"\n[PASS] MRI hop recording is working correctly.")
        # Show path details
        for count, swids in passing[:3]:   # show up to 3 examples
            path = " → ".join(f"s{sw}(q={qd})" for sw, qd in swids)
            print(f"       Path recorded: {path}")
        return True
    else:
        print(f"\n[FAIL] count was 0 in all captured packets.")
        print("       MRI egress logic may not be appending switch traces.")
        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Automated MRI P4 test")
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Drive traffic via Mininet host namespaces (requires Mininet running)",
    )
    parser.add_argument(
        "--iface",
        default=RECEIVE_IFACE,
        help=f"Interface to sniff on (default: {RECEIVE_IFACE})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=WAIT_SECONDS,
        help=f"Seconds to wait for packets (default: {WAIT_SECONDS})",
    )
    parser.add_argument(
        "--dst",
        default=SEND_HOST,
        help=f"Destination IP for test packets (default: {SEND_HOST})",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MRI Automated Test")
    print("=" * 60)
    print(f"Sniffing on  : {args.iface}")
    print(f"Capture window: {args.timeout}s")
    print()

    # Start packet capture
    print("[*] Starting packet capture ...")
    sniffer = start_sniffer(args.iface, args.timeout)

    # Generate traffic
    bg_procs = []
    if args.launch:
        bg_procs = list(run_in_mininet())
    else:
        print("[*] Sending test packets directly (no --launch flag) ...")
        # Small delay so sniffer is ready
        time.sleep(0.5)
        send_mri_packets(args.dst, PACKET_COUNT)

    # Wait for capture window to close
    print(f"[*] Waiting up to {args.timeout}s for packets ...")
    sniffer.join(timeout=args.timeout + 2)

    # Clean up background processes
    for proc in bg_procs:
        if proc and proc.poll() is None:
            proc.terminate()

    # Evaluate
    passed = evaluate_results()
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()