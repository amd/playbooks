<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 Qwen3.5-9B

Lemonade 服务器提供 Qwen3.5-9B 模型（`Qwen3.5-9B-GGUF`）。如需提前下载：

```bash
lemonade pull Qwen3.5-9B-GGUF
```

如果模型尚未下载，`lemonade run Qwen3.5-9B-GGUF` 也会在首次使用时下载模型，然后加载以进行推理。

拉取完成后，该模型会出现在 Lemonade 服务器的已下载模型列表中；下面的检查用于确认模型已存在于本机。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-9b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-9B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-9b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-9B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->
