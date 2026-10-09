<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af Gemma-4 E2B til Lemonade

Lemonade-serveren serverer Gemma-4 E2B-modellen (`Gemma-4-E2B-it-GGUF`). For at downloade den på forhånd:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` downloader også modellen ved første brug, hvis den endnu ikke er til stede, og indlæser den derefter til inferens.

Modellen vises på Lemonade-serverens liste over downloadede modeller, så snart hentningen er fuldført; tjekkene nedenfor bekræfter, at den findes på maskinen.

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