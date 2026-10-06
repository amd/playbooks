<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 為 Lemonade 下載 GPT-OSS 120B

Lemonade 伺服器提供 GPT-OSS 120B MXFP4 GGUF 模型（`gpt-oss-120b-mxfp-GGUF`）。若要事先下載該模型：

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` 也會在首次使用時下載該模型（如果尚未存在），然後將其載入以進行推論。

一旦拉取完成，該模型就會出現在 Lemonade 伺服器的已下載模型清單中；下方的檢查可確認該模型已存在於此機器上。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->