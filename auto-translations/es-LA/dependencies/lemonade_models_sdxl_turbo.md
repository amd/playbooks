<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descargando SDXL-Turbo para Lemonade

El servidor Lemonade sirve el modelo SDXL-Turbo (`SDXL-Turbo`). Para descargarlo con anticipación:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` también descarga el modelo en el primer uso si aún no está presente, y luego lo carga para la inferencia.

El modelo aparece en la lista de modelos descargados del servidor Lemonade una vez que finaliza la descarga; las siguientes verificaciones confirman que está presente en la máquina.

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