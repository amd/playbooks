<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Laste ned Qwen3 4B Hybrid for Lemonade

Lemonade-serveren betjener Qwen3 4B Hybrid-modellen (`Qwen3-4B-Hybrid`), som kjører på NPU-en og GPU-en til Ryzen AI-prosessorer. For å laste den ned på forhånd:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Modellen vises i Lemonade-serverens liste over nedlastede modeller så snart nedlastingen er fullført; kontrollen nedenfor bekrefter at den finnes på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->