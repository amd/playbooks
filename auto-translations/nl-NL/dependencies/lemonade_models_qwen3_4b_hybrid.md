<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3 4B Hybrid downloaden voor Lemonade

De Lemonade-server serveert het Qwen3 4B Hybrid-model (`Qwen3-4B-Hybrid`), dat draait op de NPU en GPU van Ryzen AI-processoren. Om het van tevoren te downloaden:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Het model verschijnt in de lijst met gedownloade modellen van de Lemonade-server zodra de pull is voltooid; de onderstaande controle bevestigt dat het aanwezig is op de machine.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->