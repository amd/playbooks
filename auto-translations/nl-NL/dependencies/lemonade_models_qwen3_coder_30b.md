<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3-Coder 30B A3B downloaden voor Lemonade

De Lemonade-server serveert het Qwen3-Coder 30B A3B-model (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Om het van tevoren te downloaden:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` downloadt het model bij het eerste gebruik ook als het nog niet aanwezig is, en laadt het vervolgens voor inferentie.

Het model verschijnt in de lijst met gedownloade modellen van de Lemonade-server zodra de pull is voltooid; de onderstaande controles bevestigen dat het aanwezig is op de machine.

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