<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Nedlasting av Gemma-4 E2B for Lemonade

Lemonade-serveren betjener Gemma-4 E2B-modellen (`Gemma-4-E2B-it-GGUF`). Slik laster du den ned på forhånd:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` laster også ned modellen ved første bruk hvis den ikke allerede finnes, og laster den deretter inn for inferens.

Modellen vises i Lemonade-serverens liste over nedlastede modeller så snart nedlastingen er fullført; kontrollene nedenfor bekrefter at den finnes på maskinen.

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