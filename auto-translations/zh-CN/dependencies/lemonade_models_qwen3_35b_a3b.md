<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 Qwen3.6 35B A3B

Lemonade 服务器提供 Qwen3.6 35B A3B 模型（`Qwen3.6-35B-A3B-GGUF`）。要提前下载该模型：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

如果首次使用时尚未下载该模型，`lemonade run Qwen3.6-35B-A3B-GGUF` 也会下载该模型，然后将其加载以进行推理。

拉取完成后，该模型将出现在 Lemonade 服务器的已下载模型列表中；下面的检查用于确认该模型已存在于本机上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-6-35b-a3b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.6-35B-A3B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->