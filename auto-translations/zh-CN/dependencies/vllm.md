<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM 通过带有 ROCm 支持的预构建容器镜像提供。请使用启动器命令，而不要直接在主机上安装 vLLM 或 PyTorch：

```bash
vllm-launch
```

该启动器会启动容器，指向集成 GPU，并在 `http://localhost:8001` 上公开与 OpenAI 兼容的 vLLM API。