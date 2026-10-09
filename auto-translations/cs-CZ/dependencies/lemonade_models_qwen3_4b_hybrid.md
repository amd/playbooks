<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stažení modelu Qwen3 4B Hybrid pro Lemonade

Server Lemonade poskytuje model Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), který běží na NPU a GPU procesorů Ryzen AI. Chcete-li jej stáhnout předem:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Model se objeví v seznamu stažených modelů serveru Lemonade, jakmile se stahování dokončí; níže uvedená kontrola ověří, že je na daném počítači přítomen.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->