<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Windows

### Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-installed, available in PATH |
| **Lemonade Server** | latest | Running on `http://localhost:13305/api/v1` |

### Lemonade LLM

The Lemonade server should be running with the device-appropriate model loaded:

| Device | Endpoint | Model |
|--------|----------|-------|
| halo / halo_box | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| stx / krk / rx7900xt / rx9070xt | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |

---

## Linux

### Prerequisites

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-installed, available in PATH |
| **Lemonade Server** | latest | Running on `http://localhost:13305/api/v1` |

### Lemonade LLM

Users are responsible for starting Lemonade with the device-appropriate model before running this playbook (see the README for the `lemonade run` command for your device).
