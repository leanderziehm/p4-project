#!/usr/bin/env python3

import subprocess

DESTINATION = "10.0.2.2"

EXPERIMENTS = [
    {
        "name": "rate_1pps",
        "count": 100,
        "interval": 1.0
    },
    {
        "name": "rate_10pps",
        "count": 100,
        "interval": 0.1
    },
    {
        "name": "rate_50pps",
        "count": 100,
        "interval": 0.02
    },
    {
        "name": "rate_100pps",
        "count": 100,
        "interval": 0.01
    }
]

for exp in EXPERIMENTS:

    print(f"\nRunning {exp['name']}")

    subprocess.run([
        "python3",
        "send.py",
        DESTINATION,
        exp["name"],
        str(exp["count"]),
        str(exp["interval"]),
        "MRI_TEST"
    ])

print("\nAll experiments completed.")