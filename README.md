# README.md

## Behavior-Aware Stateful Firewall in P4

This project implements a behavior-aware stateful firewall using the P4 programming language.
The system is designed to detect and mitigate several forms of malicious traffic inside a programmable data plane, including:

* DDoS attacks
* SYN flood attacks
* Port scanning
* ARP flooding
* High-rate HTTP abuse

The project combines:

* **P4 programmable switch logic**
* **Stateful packet tracking**
* **Dynamic blacklist enforcement**
* **Python-based control plane**
* **Mininet-based network emulation**

The environment is containerized using Podman/Docker to simplify setup and ensure reproducibility.

---

# Project Structure

```text
p4-project/
│
├── Dockerfile
├── Makefile
├── DEADLINE.md
├── TASKS_BACKLOG.md
│
├── p4src/                 # P4 source files
├── controller/            # Python control plane
├── topology/              # Mininet topology scripts
├── scripts/               # Traffic generation & testing
├── docs/                  # Report images, diagrams, notes
└── results/               # Evaluation outputs and metrics
```

---

# File Overview

## `Dockerfile`

Defines the container environment used for development and testing.

### Includes

* Ubuntu 22.04 base image
* Mininet
* Open vSwitch
* Python3
* P4 dependencies
* `p4c` compiler repository

### Purpose

Provides a reproducible networking environment for:

* P4 development
* Mininet testing
* Controller execution

---

## `Makefile`

Simplifies container management.

### Available Commands

#### Build container
Builds the image p4-mininet
```bash
make build
```
#### Run development container

```bash
make run
```

Starts a privileged container with:

* host networking
* mounted project directory
* Open vSwitch enabled

---

## `DEADLINE.md`

Contains all official course deadlines and defense information.

### Important Dates

| Event                 | Date       |
| --------------------- | ---------- |
| Project Deadline      | 07.07.2026 |
| Defense               | 08.07.2026 |
| Presentation Duration | 20 minutes |

### Defense Requirements

* Live running demo
* Explanation of architecture/design
* Questions about implementation and testing
* Mandatory attendance

---

## `TASKS_BACKLOG.md`

Main project planning and task management file.

Contains:

* Project epics
* Technical tasks
* Dependencies
* Team ownership assignments

The backlog is divided into several development phases:

1. Core Firewall
2. Stateful Tracking
3. Attack Detection
4. Enforcement Layer
5. Control Plane
6. Testing & Evaluation
7. Final Integration & Report

---

# Main Components

## `p4src/`

Contains all P4 programs.

### Responsibilities

* Packet parsing
* Forwarding logic
* Stateful registers
* Attack detection logic
* Dynamic filtering

### Expected Features

* IPv4/TCP/UDP parsing
* SYN tracking
* Port scan detection
* ARP flood monitoring
* Blacklist enforcement

---

## `controller/`

Python control-plane implementation.

### Responsibilities

* Reading switch counters/registers
* Applying detection thresholds
* Updating blacklist tables
* Runtime mitigation logic

### Technologies

* Python3
* P4Runtime APIs

---

## `topology/`

Mininet topology definitions.

### Responsibilities

* Virtual network creation
* Host and attacker setup
* Switch configuration

### Example Topologies

* Normal clients
* Multiple attackers
* Multi-host traffic scenarios

---

## `scripts/`

Traffic generation and attack simulation utilities.

### Includes

* DDoS generators
* Port scanners
* ARP flood scripts
* HTTP abuse simulation

Used for validating firewall behavior.

---

## `docs/`

Project documentation resources.

### Includes

* Architecture diagrams
* Screenshots
* Notes
* Defense material

---

## `results/`

Stores evaluation outputs.

### Includes

* Packet loss measurements
* Detection timing
* Throughput comparisons
* Benchmark results

---

# Development Workflow

## 1. Build Container

```bash
make build
```

---

## 2. Start Development Environment

```bash
make run
```

---

## 3. Compile P4 Program

Example:

```bash
p4c --target bmv2 --arch v1model firewall.p4
```

---

## 4. Run Mininet Topology

Example:

```bash
sudo python3 topology/topology.py
```

---

## 5. Start Controller

Example:

```bash
python3 controller/controller.py
```

---

## 6. Execute Attack Simulations

Example:

```bash
python3 scripts/ddos_attack.py
```

---


### Related Tasks

* T4 — Per-IP Packet Counter
* T5 — TCP State Tracking
* T6 — Port Diversity Tracker
* T8 — DDoS Detection Rules
* T9 — Port Scan Detection
* T12 — Dynamic Blacklist Table

---

# Project Goals

The goal of this project is to demonstrate how programmable data planes can provide:

* real-time attack detection
* stateful packet inspection
* adaptive filtering
* low-latency mitigation

directly inside the network switch using P4.

The project also evaluates how P4-based firewalls compare to traditional software-based approaches in responsiveness and scalability.
