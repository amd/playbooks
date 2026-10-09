<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af Qwen3 4B Hybrid til Lemonade

Lemonade-serveren serverer Qwen3 4B Hybrid-modellen (`Qwen3-4B-Hybrid`), som kører på NPU'en og GPU'en i Ryzen AI-processorer. For at downloade den på forhånd:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Modellen vises på listen over downloadede modeller i Lemonade-serveren, når hentningen er fuldført; tjekket nedenfor bekræfter, at den findes på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->