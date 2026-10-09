<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Sťahovanie Gemma-4 E2B pre Lemonade

Lemonade server poskytuje model Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Na jeho stiahnutie vopred:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` tiež stiahne model pri prvom použití, ak ešte nie je prítomný, a následne ho načíta na inferenciu.

Model sa zobrazí v zozname stiahnutých modelov na Lemonade serveri po dokončení sťahovania; kontroly uvedené nižšie potvrdia, že je na počítači prítomný.

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