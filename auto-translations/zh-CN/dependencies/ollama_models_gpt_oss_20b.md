<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Ollama 下载 GPT-OSS 20B

将 GPT-OSS 20B 模型拉取到 Ollama 中：

```bash
ollama pull gpt-oss:20b
```

拉取操作必须在 Ollama 服务器运行的情况下才能成功；如果服务器尚未运行，`ollama serve` 会启动它。

确认模型已存在：

```bash
ollama list
```

你应该能在输出中看到 `gpt-oss:20b`，以及它的大小和最后修改日期。

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->