<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade用GPT-OSS 20Bのダウンロード

Lemonadeサーバーは、GPT-OSS 20B MXFP4 GGUFモデル（`gpt-oss-20b-mxfp4-GGUF`）を提供します。事前にダウンロードするには次のようにします。

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` は、モデルがまだ存在しない場合は初回使用時にもダウンロードを行い、その後推論用にロードします。

プルが完了すると、モデルはLemonadeサーバーのダウンロード済みモデル一覧に表示されます。以下のチェックは、モデルがマシン上に存在していることを確認するものです。

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