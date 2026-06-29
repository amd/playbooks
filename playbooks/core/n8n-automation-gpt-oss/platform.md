<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Prerequisites

### Windows

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-installed and available in PATH on the AMD Ryzen™ AI Halo Developer Platform; must be manually installed on all other devices |
| **Lemonade Server** | latest | Running on `http://localhost:13305/api/v1` |

### Linux

| Component | Version | Notes |
|-----------|---------|-------|
| **Node.js** | 22.16+ | Pre-installed and available in PATH on the AMD Ryzen™ AI Halo Developer Platform; must be manually installed on all other devices |
| **Lemonade Server** | latest | Running on `http://localhost:13305/api/v1` |


## Lemonade LLM

The Lemonade server should be running with the device-appropriate model loaded (see the README for the `lemonade run` command for your device):

| Device | Endpoint | Model |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |
