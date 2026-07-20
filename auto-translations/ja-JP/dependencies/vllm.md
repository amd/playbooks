<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### vLLM

vLLMはROCm対応のビルド済みコンテナイメージとして提供されています。ホストに直接vLLMやPyTorchをインストールするのではなく、ランチャーコマンドを使用してください。

```bash
vllm-launch
```

このランチャーはコンテナを起動し、統合GPUを対象として、OpenAI互換のvLLM APIを`http://localhost:8001`で公開します。