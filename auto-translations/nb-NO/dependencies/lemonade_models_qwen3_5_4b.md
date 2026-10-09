<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Laste ned Qwen3.5 4B for Lemonade

Lemonade-serveren betjener Qwen3.5 4B-modellen (`Qwen3.5-4B-GGUF`). For å laste den ned på forhånd:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` laster også ned modellen ved første bruk hvis den ikke allerede er til stede, og laster den deretter inn for inferens.

Modellen vises i Lemonade-serverens liste over nedlastede modeller så snart nedlastingen er fullført; kontrollene nedenfor bekrefter at den er til stede på maskinen.

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