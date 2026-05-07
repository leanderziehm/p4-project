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

# File Overview

## `Dockerfile`
requires podman installed

---



# Main Components

# Development Workflow
## `Makefile`
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

## 3. run

---
???
---

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


# Project Goals

The goal of this project is to demonstrate how programmable data planes can provide:

* real-time attack detection
* stateful packet inspection
* adaptive filtering
* low-latency mitigation

directly inside the network switch using P4.

The project also evaluates how P4-based firewalls compare to traditional software-based approaches in responsiveness and scalability.
