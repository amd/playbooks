<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 為 Lemonade 下載 GPT-OSS 20B

Lemonade 伺服器提供 GPT-OSS 20B MXFP4 GGUF 模型（`gpt-oss-20b-mxfp4-GGUF`）。若要提前下載，請：

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` 在首次使用時，若模型尚未存在，也會自動下載該模型，然後將其載入以進行推論。

一旦拉取完成，該模型就會出現在 Lemonade 伺服器的已下載模型清單中；以下檢查可確認該模型已存在於機器上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->