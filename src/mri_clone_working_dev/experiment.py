#!/usr/bin/env python3
import subprocess
import random
import json
import time

# -----------------------------
# Load topology hosts
# -----------------------------
def load_ips_from_topology(path="topology.json"):
    with open(path, "r") as f:
        topo = json.load(f)

    hosts = []
    for name, data in topo["hosts"].items():
        ip = data["ip"].split("/")[0]
        # hosts.append((name, ip))
        hosts.append(ip)

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


def random_paragraph(min_sent=1, max_sent=1500):
    return " ".join(random.choice(SENTENCES) for _ in range(random.randint(min_sent, max_sent)))


def random_noise_text(min_words=3, max_words=1500):
    return " ".join(
        random.choice(WORDS)
        for _ in range(random.randint(min_words, max_words))
    )


def generate_payload():
    mode = random.choice(["sentences", "words"])
    if mode == "sentences":
        return random_paragraph()
    else:
        return random_noise_text()

# -----------------------------
# Experiments
# -----------------------------
EXPERIMENTS = [
    # {"name": "rate_100pps", "count": 10000, "interval":3},
    {"name": "rate_100pps", "count": 99999999, "interval": 0.001,"amount": 500},
]
    # {"name": "rate_1pps", "count": 50, "interval": 1.0},
    # {"name": "rate_10pps", "count": 50, "interval": 0.1},
    # {"name": "rate_50pps", "count": 50, "interval": 0.02},
    # {"name": "rate_100pps", "count": 50, "interval": 0.01},


def main():
    TELEMETRY_HOST = "10.0.3.3"
    ips = load_ips_from_topology("topology.json")
    print(f"ips: {ips}")
    ips.remove(TELEMETRY_HOST)
    for exp in EXPERIMENTS:
        for i in range(exp["count"]):
            name = str(exp['name'])
            count = exp['count']
            interval = exp['interval']
            amount = str(exp['amount'])
            print(f"\n=== Running {exp['name']} ===")
            ip = random.choice(ips)
            payload = generate_payload()
            payload = payload.replace("\n", " ")
            max_len = 1353
            payload = payload[:max_len]
            time.sleep(interval)
            print(f"[n={name}]/c={count} i={interval} -> ({ip}) ")

            subprocess.run([
                "python3",
                "send.py",
                ip,
                exp["name"] + payload, 
                amount,
                str(interval)
            ])

    print("\nAll experiments completed.")


if __name__ == "__main__":
    main()