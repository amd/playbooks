<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descargando Qwen3 4B Hybrid para Lemonade

El servidor Lemonade entrega el modelo Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), que se ejecuta en el NPU y la GPU de los procesadores Ryzen AI. Para descargarlo con anticipación:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

El modelo aparece en la lista de modelos descargados del servidor Lemonade una vez que se completa la descarga; la verificación a continuación confirma que está presente en la máquina.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->