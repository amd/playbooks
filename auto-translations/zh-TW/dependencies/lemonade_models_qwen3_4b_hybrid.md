<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 為 Lemonade 下載 Qwen3 4B Hybrid

Lemonade 伺服器提供 Qwen3 4B Hybrid 模型(`Qwen3-4B-Hybrid`),可在 Ryzen AI 處理器的 NPU 和 GPU 上執行。若要事先下載:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

提取完成後,該模型會出現在 Lemonade 伺服器的已下載模型清單中;下方的檢查可確認其是否已存在於此機器上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->