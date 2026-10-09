<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 下載 GPT-OSS 20B 供 Ollama 使用

將 GPT-OSS 20B 模型拉取到 Ollama：

```bash
ollama pull gpt-oss:20b
```

Ollama 伺服器必須處於執行狀態，拉取作業才能成功；若尚未執行，`ollama serve` 會啟動它。

確認模型已存在：

```bash
ollama list
```

您應該會在輸出中看到 `gpt-oss:20b`，以及其大小和最後修改日期。

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->