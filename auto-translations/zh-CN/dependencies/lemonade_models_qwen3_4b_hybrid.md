<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 为 Lemonade 下载 Qwen3 4B Hybrid 模型

Lemonade 服务器提供 Qwen3 4B Hybrid 模型（`Qwen3-4B-Hybrid`），该模型可在 Ryzen AI 处理器的 NPU 和 GPU 上运行。要提前下载它：

```powershell
lemonade pull Qwen3-4B-Hybrid
```

拉取完成后，该模型会出现在 Lemonade 服务器的已下载模型列表中；下面的检查可确认该模型已存在于本机上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->