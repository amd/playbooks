<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM 通过预构建的支持 ROCm 的容器镜像提供。请使用启动器命令，而非直接在主机上安装 vLLM 或 PyTorch：

```bash
vllm-launch
```

启动器将启动容器，以集成 GPU 为目标，并在 `http://localhost:8001` 上公开与 OpenAI 兼容的 vLLM API。