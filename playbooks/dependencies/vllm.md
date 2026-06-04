<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM is provided through a prebuilt container image with ROCm support. Use the launcher command instead of installing vLLM or PyTorch directly on the host:

```bash
vllm-launch
```

The launcher starts the container, targets the integrated GPU, and exposes the OpenAI-compatible vLLM API on `http://localhost:8001`.
