<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade用のQwen3.6 35B A3Bのダウンロード

Lemonadeサーバーは、Qwen3.6 35B A3Bモデル(`Qwen3.6-35B-A3B-GGUF`)を提供します。事前にダウンロードするには、以下の手順に従ってください。

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF`は、モデルがまだ存在しない場合、初回使用時にもモデルをダウンロードし、その後推論用にロードします。

プルが完了すると、モデルはLemonadeサーバーのダウンロード済みモデルリストに表示されます。以下の確認手順により、モデルがこのマシン上に存在していることを確認できます。

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