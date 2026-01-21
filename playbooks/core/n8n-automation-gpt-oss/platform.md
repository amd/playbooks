# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Windows

### Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 20.x+ | Pre-installed, available in PATH |
| **Lemonade Server** | latest | Running on `http://localhost:8000/v1` |

### Lemonade LLM

The Lemonade server should be running with Qwen 4B loaded:

| Service | Endpoint | Model |
|---------|----------|-------|
| **Lemonade API** | `http://localhost:8000/v1` | Qwen3-4B |

---

## Linux

### Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 20.x+ | Pre-installed, available in PATH |
| **Lemonade Server** | latest | Running on `http://localhost:8000/v1` |

### Lemonade LLM

Users are responsible for starting Lemonade with Qwen 4B before running this playbook.
