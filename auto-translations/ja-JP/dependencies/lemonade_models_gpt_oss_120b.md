<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade用のGPT-OSS 120Bのダウンロード

Lemonadeサーバーは、GPT-OSS 120B MXFP4 GGUFモデル（`gpt-oss-120b-mxfp-GGUF`）を提供します。事前にダウンロードするには、次のようにします。

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` は、初回使用時にモデルがまだ存在しない場合にもダウンロードを行い、その後推論のためにロードします。

プルが完了すると、Lemonadeサーバーのダウンロード済みモデルの一覧にモデルが表示されます。以下のチェックは、モデルがマシン上に存在することを確認するものです。

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