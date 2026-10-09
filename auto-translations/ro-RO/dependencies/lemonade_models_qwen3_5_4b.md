<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea Qwen3.5 4B pentru Lemonade

Serverul Lemonade servește modelul Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Pentru a-l descărca în prealabil:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

`lemonade run Qwen3.5-4B-GGUF` descarcă de asemenea modelul la prima utilizare, dacă nu este deja prezent, apoi îl încarcă pentru inferență.

Modelul apare în lista de modele descărcate a serverului Lemonade odată ce descărcarea este finalizată; verificările de mai jos confirmă prezența acestuia pe mașină.

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