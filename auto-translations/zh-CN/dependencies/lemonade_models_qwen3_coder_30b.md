<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 Qwen3-Coder 30B A3B

Lemonade 服务器提供 Qwen3-Coder 30B A3B 模型（`Qwen3-Coder-30B-A3B-Instruct-GGUF`）。要提前下载它：

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

如果模型尚未存在，`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` 也会在首次使用时下载该模型，然后将其加载以进行推理。

下载完成后，该模型会出现在 Lemonade 服务器的已下载模型列表中；下面的检查可确认它已存在于该机器上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->