<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje modela Qwen3 4B Hybrid za Lemonade

Lemonade server opslužuje model Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), koji se izvršava na NPU i GPU procesorima Ryzen AI. Da biste ga preuzeli unapred:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Model se pojavljuje na listi preuzetih modela Lemonade servera čim se preuzimanje završi; provera ispod potvrđuje da je prisutan na mašini.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->