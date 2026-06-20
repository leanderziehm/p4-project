#!/usr/bin/env python3
import subprocess
import random
import json
import os

# -----------------------------
# Load topology hosts
# -----------------------------
def load_hosts(path="topology.json"):
    with open(path, "r") as f:
        topo = json.load(f)

    hosts = []
    for name, data in topo["hosts"].items():
        ip = data["ip"].split("/")[0]
        hosts.append((name, ip))

    return hosts


# -----------------------------
# Random payload generator
# -----------------------------
SENTENCES = [
    "The network experiment is running smoothly across multiple switches.",
    "Packet timing variations are being observed under different loads.",
    "Latency measurements are collected for each transmission burst.",
    "Traffic engineering helps understand congestion behavior in the topology.",
    "Switch pipelines process packets based on installed rules.",
    "Queue buildup is influenced by bursty traffic patterns.",
    "Flow scheduling impacts end-to-end delay across the network."
]

WORDS = [
    "latency", "throughput", "queue", "switch", "packet", "routing",
    "congestion", "buffer", "pipeline", "flow", "experiment",
    "telemetry", "jitter", "bandwidth", "drop", "forwarding"
]


def random_sentence():
    return random.choice(SENTENCES)


def random_paragraph(min_sent=1, max_sent=50):
    return " ".join(
        random_sentence()
        for _ in range(random.randint(min_sent, max_sent))
    )


def random_noise_text(min_words=3, max_words=30):
    return " ".join(
        random.choice(WORDS)
        for _ in range(random.randint(min_words, max_words))
    )


def generate_payload():
    mode = random.choice(["sentence", "paragraph", "noise"])
    if mode == "sentence":
        return random_sentence()
    elif mode == "paragraph":
        return random_paragraph()
    else:
        return random_noise_text()


# -----------------------------
# Experiments
# -----------------------------
EXPERIMENTS = [
    {"name": "rate_1pps", "count": 50, "interval": 1.0},
    {"name": "rate_10pps", "count": 50, "interval": 0.1},
    {"name": "rate_50pps", "count": 50, "interval": 0.02},
    {"name": "rate_100pps", "count": 50, "interval": 0.01},
]


def main():
    hosts = load_hosts("topology.json")

    if not hosts:
        print("No hosts found in topology.json")
        return

    print("Loaded hosts:")
    for h in hosts:
        print(f" - {h[0]} -> {h[1]}")

    print("\nStarting experiments...\n")

    for exp in EXPERIMENTS:
        print(f"\n=== Running {exp['name']} ===")

        for i in range(exp["count"]):

            # pick random destination host
            host_name, ip = random.choice(hosts)

            # generate payload
            payload = generate_payload()

            # optional: keep payload single-line safe
            payload = payload.replace("\n", " ")

            print(f"[{exp['name']}] {i+1}/{exp['count']} -> {host_name} ({ip})")

            subprocess.run([
                "python3",
                "send.py",
                ip,
                exp["name"],
                "1",  # send one packet per iteration
                str(exp["interval"]),
                payload
            ])

    print("\nAll experiments completed.")


if __name__ == "__main__":
    main()