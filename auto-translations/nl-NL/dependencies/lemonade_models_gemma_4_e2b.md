<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Het downloaden van Gemma-4 E2B voor Lemonade

De Lemonade-server host het Gemma-4 E2B-model (`Gemma-4-E2B-it-GGUF`). Om het vooraf te downloaden:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` downloadt het model bij het eerste gebruik ook automatisch als het nog niet aanwezig is, en laadt het vervolgens voor inferentie.

Het model verschijnt in de lijst met gedownloade modellen van de Lemonade-server zodra het ophalen is voltooid; de onderstaande controles bevestigen dat het aanwezig is op de machine.

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