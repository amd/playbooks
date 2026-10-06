<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie modelu Qwen3-Coder 30B A3B pre Lemonade

Lemonade server sprístupňuje model Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Ak ho chcete stiahnuť vopred:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

Príkaz `lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` tiež stiahne model pri prvom použití, ak ešte nie je stiahnutý, a následne ho načíta na inferenciu.

Model sa zobrazí v zozname stiahnutých modelov na Lemonade serveri hneď po dokončení sťahovania; nasledujúce kontroly potvrdzujú, že sa nachádza v zariadení.

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