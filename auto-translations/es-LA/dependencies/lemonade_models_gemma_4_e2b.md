<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descarga de Gemma-4 E2B para Lemonade

El servidor Lemonade sirve el modelo Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Para descargarlo con anticipación:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` también descarga el modelo la primera vez que se usa, si aún no está presente, y luego lo carga para inferencia.

El modelo aparece en la lista de modelos descargados del servidor Lemonade una vez que finaliza la descarga; las siguientes verificaciones confirman que está presente en la máquina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gemma-4-e2b-it-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Gemma-4-E2B-it-GGUF
```
<!-- @test:end -->
<!-- @os:end -->