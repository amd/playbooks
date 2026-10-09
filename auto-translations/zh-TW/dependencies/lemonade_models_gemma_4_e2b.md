<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 為 Lemonade 下載 Gemma-4 E2B

Lemonade 伺服器提供 Gemma-4 E2B 模型（`Gemma-4-E2B-it-GGUF`）。若要提前下載：

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` 若模型尚未存在，也會在首次使用時下載該模型，然後載入以進行推論。

一旦下載完成，該模型就會出現在 Lemonade 伺服器的已下載模型清單中；以下檢查可確認該模型已存在於此機器上。

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