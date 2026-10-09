<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea modelului Qwen3-Coder 30B A3B pentru Lemonade

Serverul Lemonade servește modelul Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Pentru a-l descărca în prealabil:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

`lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` descarcă de asemenea modelul la prima utilizare, dacă acesta nu este deja prezent, apoi îl încarcă pentru inferență.

Modelul apare în lista de modele descărcate a serverului Lemonade odată ce descărcarea se finalizează; verificările de mai jos confirmă că este prezent pe mașină.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-qwen3-coder-30b-a3b-instruct-gguf-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q Qwen3-Coder-30B-A3B-Instruct-GGUF
```
<!-- @test:end -->
<!-- @os:end -->