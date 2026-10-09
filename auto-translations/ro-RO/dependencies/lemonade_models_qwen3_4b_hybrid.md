<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea Qwen3 4B Hybrid pentru Lemonade

Serverul Lemonade pune la dispoziție modelul Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), care rulează pe NPU și GPU ale procesoarelor Ryzen AI. Pentru a-l descărca în prealabil:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Modelul apare în lista de modele descărcate a serverului Lemonade odată ce descărcarea (pull) s-a finalizat; verificarea de mai jos confirmă prezența lui pe mașină.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->