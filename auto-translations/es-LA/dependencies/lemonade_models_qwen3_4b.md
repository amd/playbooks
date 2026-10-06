<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descarga de Qwen3.5 4B para Lemonade

El servidor Lemonade sirve el modelo Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Para descargarlo con anticipación:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` también descarga el modelo en el primer uso si aún no está presente, y luego lo carga para inferencia.

El modelo aparece en la lista de modelos descargados del servidor Lemonade una vez que finaliza la descarga; las verificaciones a continuación confirman que está presente en la máquina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-5-4b-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3.5-4B-GGUF
```
<!-- @test:end -->
<!-- @os:end -->