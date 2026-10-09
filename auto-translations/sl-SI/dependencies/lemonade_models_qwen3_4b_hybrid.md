<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos modela Qwen3 4B Hybrid za Lemonade

Strežnik Lemonade streže model Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), ki deluje na NPU in GPU procesorjih Ryzen AI. Za predhodni prenos:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Model se prikaže na seznamu prenesenih modelov strežnika Lemonade, ko je prenos končan; spodnje preverjanje potrdi, da je prisoten v napravi.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->