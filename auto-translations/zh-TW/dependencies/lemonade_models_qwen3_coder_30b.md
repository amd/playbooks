<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 下載 Qwen3-Coder 30B A3B 供 Lemonade 使用

Lemonade 伺服器提供 Qwen3-Coder 30B A3B 模型(`Qwen3-Coder-30B-A3B-Instruct-GGUF`)服務。若要提前下載該模型：

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

若模型尚未存在，`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` 也會在首次使用時下載模型，然後載入以進行推論。

一旦下載完成，該模型就會出現在 Lemonade 伺服器的已下載模型清單中；以下檢查可確認其已存在於機器上。

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