<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 為 Lemonade 下載 Qwen3.6 35B A3B

Lemonade 伺服器提供 Qwen3.6 35B A3B 模型（`Qwen3.6-35B-A3B-GGUF`）。若要提前下載：

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

若尚未下載該模型，`lemonade run Qwen3.6-35B-A3B-GGUF` 也會在首次使用時下載模型，然後載入以進行推論。

一旦提取完成，該模型就會出現在 Lemonade 伺服器的已下載模型清單中；以下檢查可確認該模型已存在於此機器上。

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