<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM 是透過內建 ROCm 支援的預先建置容器映像檔提供的。請使用啟動器命令，而不是直接在主機上安裝 vLLM 或 PyTorch：

```bash
vllm-launch
```

此啟動器會啟動容器、鎖定內建 GPU，並在 `http://localhost:8001` 上公開與 OpenAI 相容的 vLLM API。