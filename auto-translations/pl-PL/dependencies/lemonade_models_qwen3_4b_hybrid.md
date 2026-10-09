<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu Qwen3 4B Hybrid dla Lemonade

Serwer Lemonade udostępnia model Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), który działa na NPU i GPU procesorów Ryzen AI. Aby pobrać go z wyprzedzeniem:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Model pojawi się na liście pobranych modeli serwera Lemonade po zakończeniu pobierania; poniższa weryfikacja potwierdza jego obecność na maszynie.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->