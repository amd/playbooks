<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3.5 4B downloaden voor Lemonade

De Lemonade-server bedient het Qwen3.5 4B-model (`Qwen3.5-4B-GGUF`). Om het van tevoren te downloaden:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` downloadt het model bij het eerste gebruik ook als het nog niet aanwezig is, en laadt het vervolgens voor inferentie.

Het model verschijnt in de lijst met gedownloade modellen van de Lemonade-server zodra het ophalen is voltooid; de onderstaande controles bevestigen dat het aanwezig is op de machine.

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