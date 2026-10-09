<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie Qwen3 4B Hybrid pre Lemonade

Server Lemonade poskytuje model Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), ktorý beží na NPU a GPU procesorov Ryzen AI. Na jeho predčasné stiahnutie:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Model sa zobrazí v zozname stiahnutých modelov na serveri Lemonade po dokončení sťahovania; nasledujúca kontrola potvrdí, že sa nachádza na danom počítači.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->