<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Platform Configuration

This document describes the expected platform configurations for running this playbook.

## Required Apps/Frameworks

### Windows/Linux

- **Lemonade Server** should be installed following the
  [Lemonade installation guide](https://lemonade-server.ai/docs/guide/install/).
- **Node.js 22.12 or later** and `npm`, used by the `agent-canvas` CLI and MCP
  servers launched with `npx`.
- **uv**, the Python package manager that Agent Canvas uses to manage the agent
  server environment. Install it from the
  [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

## Required Models

### Windows/Linux

The following model must be available to Lemonade Server before starting the
playbook.

| Model Type | Model ID | Notes |
| --- | --- | --- |
| GGUF chat model | `Qwen3.6-35B-A3B-GGUF` | Served by Lemonade Server on `http://127.0.0.1:13305/api/v1`. Use a smaller GGUF model on devices with less than 32 GB of memory. |

Start the model with:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```

## External Credentials

This playbook requires:

- A GitHub token with read access to the repository being summarized.
- A Slack bot token with `chat:write` and channel read access.
- A Slack team ID and the target Slack channel ID.
