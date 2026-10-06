<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Laste ned Qwen3.6 35B A3B for Lemonade

Lemonade-serveren betjener Qwen3.6 35B A3B-modellen (`Qwen3.6-35B-A3B-GGUF`). Slik laster du den ned på forhånd:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` laster også ned modellen ved første bruk hvis den ikke allerede finnes, og laster den deretter inn for inferens.

Modellen vises i Lemonade-serverens liste over nedlastede modeller når nedlastingen er fullført; kontrollene nedenfor bekrefter at den finnes på maskinen.

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