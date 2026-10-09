<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner Qwen3 4B Hybrid för Lemonade

Lemonade-servern tillhandahåller modellen Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), som körs på NPU:n och GPU:n i Ryzen AI-processorer. För att ladda ner den i förväg:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Modellen visas i Lemonade-serverns lista över nedladdade modeller när hämtningen är klar; kontrollen nedan bekräftar att den finns på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->