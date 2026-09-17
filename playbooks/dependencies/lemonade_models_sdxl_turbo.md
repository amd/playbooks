<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Downloading SDXL-Turbo for Lemonade

The Lemonade server serves the SDXL-Turbo model (`SDXL-Turbo`). To download it ahead of time:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` also downloads the model on first use if it is not already present, then loads it for inference.

The model appears in the Lemonade server's downloaded-model list once the pull completes; the checks below confirm it is present on the machine.

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
