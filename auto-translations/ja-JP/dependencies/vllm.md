<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLM は ROCm サポートを含むビルド済みコンテナイメージとして提供されています。ホストに vLLM や PyTorch を直接インストールする代わりに、ランチャーコマンドを使用してください：

```bash
vllm-launch
```

ランチャーはコンテナを起動し、統合 GPU をターゲットとして、OpenAI 互換の vLLM API を `http://localhost:8001` で公開します。