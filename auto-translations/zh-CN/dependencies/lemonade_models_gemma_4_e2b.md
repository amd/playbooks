<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 Gemma-4 E2B

Lemonade 服务器提供 Gemma-4 E2B 模型（`Gemma-4-E2B-it-GGUF`）。要提前下载它：

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

如果 `Gemma-4-E2B-it-GGUF` 模型尚未存在，`lemonade run Gemma-4-E2B-it-GGUF` 也会在首次使用时下载该模型，然后加载它以进行推理。

拉取完成后，该模型会出现在 Lemonade 服务器的已下载模型列表中；下面的检查用于确认它已存在于该机器上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->