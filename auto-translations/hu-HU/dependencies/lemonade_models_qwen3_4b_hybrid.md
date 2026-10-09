<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Qwen3 4B Hybrid modell letöltése a Lemonade-hez

A Lemonade szerver a Qwen3 4B Hybrid modellt (`Qwen3-4B-Hybrid`) szolgálja ki, amely a Ryzen AI processzorok NPU-ján és GPU-ján fut. Előzetes letöltéshez:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

A modell a letöltés befejezése után megjelenik a Lemonade szerver letöltött modelleket tartalmazó listájában; az alábbi ellenőrzés megerősíti, hogy jelen van a gépen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->