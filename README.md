# Distributed and Parallel Computing Lab

This repository contains implementations for **Distributed and Parallel Computing** laboratory experiments.  
Each lab is organized to demonstrate core **client–server architectures and communication models** using Python.

---

## Repository Structure
---
Distributed-Parallel-Computing-Lab/
│
├── Lab1/
│ 
│ 
│ 
│
├── Lab2/
│ 
│ 
│ 
│ 
│
└── README.md



---

## Lab 1: RPC and Socket Programming

### Objective
To understand **basic distributed communication** using:
- Remote Procedure Call (RPC)
- TCP Socket Programming

### Experiments
- RPC-based palindrome and armstrong number checking
- RPC-based matrix multiplication
- Socket-based command server (TIME, ECHO, EXIT)
- Socket-based matrix multiplication using JSON

### Key Concepts
- Client–server model
- RPC mechanism
- Data serialization
- Multi-client handling using threads

---

## Lab 2: Client–Server Architectures

### Objective
To study different **client–server architectures** and their scalability.

### Architectures Implemented

#### 1. Single Server – Multiple Clients (SS–MC)
- One server listens on a single port
- Multiple clients connect simultaneously
- Server uses multithreading to handle clients

**Files**
- `MCSS_Server.py`
- `MCSS_Client.py`

#### 2. Multiple Servers – Multiple Clients (MS–MC)
- Multiple servers run on different ports
- Clients can connect to any server
- Better scalability and fault tolerance

**Files**
- `MCMS_server.py`
- `MCMS_client.py`

### Key Concepts
- Thread-per-client model
- Server scalability limits
- Distributed request handling
- Basic load distribution

---

## How to Run (General)

1. Start the required server program first.
2. Run one or more client programs in separate terminals.
3. Follow on-screen instructions to interact with the server.

---

## Learning Outcomes

- Understand distributed system basics
- Compare RPC vs Socket communication
- Analyze single-server vs multi-server architectures
- Learn scalability and fault-tolerance trade-offs
- Build foundations for real distributed systems

---

## Note

These implementations are **educational** and meant for lab understanding.  
They do not include real load balancers, async I/O, or production-level fault tolerance.

---
