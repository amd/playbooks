<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af Qwen3.5 4B til Lemonade

Lemonade-serveren serverer Qwen3.5 4B-modellen (`Qwen3.5-4B-GGUF`). Sådan downloader du den på forhånd:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` downloader også modellen ved første brug, hvis den ikke allerede findes, og indlæser den derefter til inferens.

Modellen vises på listen over downloadede modeller i Lemonade-serveren, når download er fuldført; tjekkene nedenfor bekræfter, at den er til stede på maskinen.

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