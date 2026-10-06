<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af SDXL-Turbo til Lemonade

Lemonade-serveren serverer SDXL-Turbo-modellen (`SDXL-Turbo`). For at downloade den på forhånd:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` downloader også modellen ved første brug, hvis den ikke allerede findes, og indlæser den derefter til inferens.

Modellen vises på Lemonade-serverens liste over downloadede modeller, når hentningen er fuldført; nedenstående kontroller bekræfter, at den findes på maskinen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->