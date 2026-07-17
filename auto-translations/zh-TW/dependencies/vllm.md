<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM 透過內建 ROCm 支援的預建容器映像檔提供。請使用啟動器命令，而非直接在主機上安裝 vLLM 或 PyTorch：

```bash
vllm-launch
```

啟動器會啟動容器、以整合式 GPU 為目標，並在 `http://localhost:8001` 上公開與 OpenAI 相容的 vLLM API。