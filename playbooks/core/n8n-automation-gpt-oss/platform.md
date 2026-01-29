# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Windows

### Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 20.x+ | Pre-installed, available in PATH |
| **Lemonade Server** | latest | Running on `http://localhost:8000/api/v1` |

### Lemonade LLM

The Lemonade server should be running with gpt-oss-20b loaded:

| Service | Endpoint | Model |
|---------|----------|-------|
| **Lemonade API** | `http://localhost:8000/api/v1` | gpt-oss-120b-mxfp4-GGUF |

---

## Linux

### Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 20.x+ | Pre-installed, available in PATH |
| **Lemonade Server** | latest | Running on `http://localhost:8000/api/v1` |

### Lemonade LLM

Users are responsible for starting Lemonade with gpt-oss-20b before running this playbook.
