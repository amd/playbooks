<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea Gemma-4 E2B pentru Lemonade

Serverul Lemonade servește modelul Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Pentru a-l descărca în prealabil:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` descarcă de asemenea modelul la prima utilizare, dacă acesta nu este deja prezent, apoi îl încarcă pentru inferență.

Modelul apare în lista de modele descărcate a serverului Lemonade odată ce descărcarea se finalizează; verificările de mai jos confirmă că este prezent pe mașină.

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