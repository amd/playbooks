<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Sťahovanie Qwen3.6 35B A3B pre Lemonade

Lemonade server poskytuje model Qwen3.6 35B A3B (`Qwen3.6-35B-A3B-GGUF`). Na jeho stiahnutie vopred:

```bash
lemonade pull Qwen3.6-35B-A3B-GGUF
```

`lemonade run Qwen3.6-35B-A3B-GGUF` tiež stiahne model pri prvom použití, ak ešte nie je prítomný, a následne ho načíta na inferenciu.

Model sa v zozname stiahnutých modelov Lemonade servera objaví po dokončení sťahovania; nasledujúce kontroly potvrdzujú, že sa nachádza na počítači.

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