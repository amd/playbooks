<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade用のQwen3-Coder 30B A3Bのダウンロード

Lemonadeサーバーは、Qwen3-Coder 30B A3Bモデル(`Qwen3-Coder-30B-A3B-Instruct-GGUF`)を提供します。事前にダウンロードするには、次のようにします。

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF`は、モデルがまだ存在しない場合、初回使用時にもモデルをダウンロードし、その後推論用にロードします。

プルが完了すると、Lemonadeサーバーのダウンロード済みモデルのリストにそのモデルが表示されます。以下のチェックは、マシン上にそのモデルが存在することを確認するものです。

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