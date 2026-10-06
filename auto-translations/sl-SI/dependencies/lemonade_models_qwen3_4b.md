<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos modela Qwen3.5 4B za Lemonade

Strežnik Lemonade streže model Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Za vnaprejšnji prenos:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

Ukaz `lemonade run Qwen3.5-4B-GGUF` ob prvi uporabi prav tako prenese model, če ta še ni prisoten, nato pa ga naloži za sklepanje.

Model se prikaže na seznamu prenesenih modelov strežnika Lemonade, ko je prenos zaključen; spodnja preverjanja potrdijo, da je prisoten v napravi.

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