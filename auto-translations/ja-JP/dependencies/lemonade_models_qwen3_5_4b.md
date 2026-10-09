<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade用のQwen3.5 4Bのダウンロード

Lemonadeサーバーは、Qwen3.5 4Bモデル(`Qwen3.5-4B-GGUF`)を提供します。事前にダウンロードするには:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF`は、モデルがまだ存在しない場合、初回使用時にもモデルをダウンロードし、その後推論用にロードします。

ダウンロードが完了すると、モデルはLemonadeサーバーのダウンロード済みモデル一覧に表示されます。以下のチェックは、モデルがマシン上に存在することを確認するものです。

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->