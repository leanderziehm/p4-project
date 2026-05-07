# 🧩 Project Backlog

Description:
Behavior-Aware Stateful Firewall for DDoS, Scanning, and Traffic Abuse Detection in P4

Abreviations: 
Task as T
Juan as J or Leander as L


## EPIC 1 — Core P4 Firewall (Foundation)

### T1 — Packet Parsing

* Ethernet header
* IPv4 header
* TCP / UDP headers
* ARP header

**Owner:** ?

---

### T2 — Basic Forwarding Pipeline

* L2/L3 forwarding tables
* MAC rewrite actions
* basic drop/allow logic

**Dependency:** T1
**Owner:** ?

---

### T3 — Table Design (ACL + Forwarding)

* IP allow/deny table
* port-based allow/deny table
* default drop behavior

**Dependency:** T2
**Owner:** ?

---

# 🧠 EPIC 2 — Stateful Tracking Engine (Shared core logic)

### T4 — Per-IP Packet Counter

* register: packets per source IP
* update on every packet

**Dependency:** T1/T2
**Owner:** ?

---

### T5 — TCP State Tracking (SYN monitoring)

* count SYN packets per IP
* detect incomplete handshakes

**Dependency:** T4
**Owner:** ?

---

### T6 — Port Diversity Tracker (scan detection base)

* track how many destination ports per source IP
* detect scanning behavior

**Dependency:** T4
**Owner:** ?

---

### T7 — ARP Request Tracker

* count ARP requests per IP/MAC
* detect ARP flooding

**Dependency:** T1
**Owner:** ?

---

# 🚨 EPIC 3 — Attack Detection Logic

### T8 — DDoS Detection Rules

* threshold on packet rate
* SYN flood detection logic
* mark IP as malicious

**Dependency:** T4/T5
**Owner:** ?

---

### T9 — Port Scan Detection

* many ports per source IP threshold
* scanner classification

**Dependency:** T6
**Owner:** ?

---

### T10 — ARP Flood Detection

* ARP request rate threshold
* block/limit logic

**Dependency:** T7
**Owner:** ?

---

### T11 — Bot-like HTTP Abuse Detection (approx)

* high-rate traffic on ports 80/443
* burst detection per IP

**Dependency:** T4
**Owner:** ?

---

# 🛑 EPIC 4 — Enforcement / Mitigation Layer

### T12 — Dynamic Blacklist Table

* add/remove IPs at runtime
* used by all detectors

**Dependency:** T3
**Owner:** ?

---

### T13 — Rate Limiting Mechanism

* per-IP packet throttling
* soft drop behavior

**Dependency:** T4/T12
**Owner:** ?

---

### T14 — Attack Response Logic Integration

* connect detection → blacklist
* enforce drop rules

**Dependency:** T8/T9/T10/T11/T12
**Owner:** ? + B (integration task)

---

# 🌐 EPIC 5 — Control Plane (Python / P4Runtime)

### T15 — Controller Skeleton

* connect to switch
* read counters/registers

**Owner:** ?

---

### T16 — Threshold Decision Engine

* decide:

  * DDoS → block IP
  * scan → block IP
  * ARP flood → limit

**Dependency:** T15
**Owner:** ?

---

### T17 — Rule Push System

* install blacklist entries dynamically
* update tables in P4 switch

**Dependency:** T16
**Owner:** ?

---

# 🧪 EPIC 6 — Mininet + Testing

### T18 — Mininet Topology

* multiple hosts
* attacker + normal clients
* switch setup

**Owner:** ?

---

### T19 — Traffic Generator Scripts

* DDoS simulation script
* port scanner script
* ARP flood script

**Owner:** ?

---

### T20 — Evaluation + Metrics

* packet loss graphs
* detection time
* throughput comparison

**Owner:** ?

---

# 📄 EPIC 7 — Integration & Report

### T21 — System Integration

* ensure P4 + controller + Mininet work together

**Owner:** ?

---

### T22 — Final Report Writing

* architecture explanation
* attack descriptions
* results + screenshots

**Owner:** ?
