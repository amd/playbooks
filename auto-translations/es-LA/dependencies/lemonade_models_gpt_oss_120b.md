<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descarga de GPT-OSS 120B para Lemonade

El servidor Lemonade sirve el modelo GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Para descargarlo con anticipación:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` también descarga el modelo en el primer uso si aún no está presente, y luego lo carga para la inferencia.

El modelo aparece en la lista de modelos descargados del servidor Lemonade una vez que finaliza la descarga; las verificaciones a continuación confirman que está presente en la máquina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-120b-mxfp-GGUF
```
<!-- @test:end -->
<!-- @os:end -->