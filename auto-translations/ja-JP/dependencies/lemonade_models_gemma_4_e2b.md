<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade用Gemma-4 E2Bのダウンロード

Lemonadeサーバーは、Gemma-4 E2Bモデル(`Gemma-4-E2B-it-GGUF`)を提供します。事前にダウンロードするには次のようにします。

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF`は、モデルがまだ存在しない場合は初回使用時にもダウンロードを行い、その後推論のために読み込みます。

プルが完了すると、モデルはLemonadeサーバーのダウンロード済みモデル一覧に表示されます。以下の確認手順で、モデルがマシン上に存在していることを確認します。

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