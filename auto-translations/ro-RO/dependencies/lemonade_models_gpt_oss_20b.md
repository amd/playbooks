<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea GPT-OSS 20B pentru Lemonade

Serverul Lemonade servește modelul GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Pentru a-l descărca în prealabil:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

`lemonade run gpt-oss-20b-mxfp4-GGUF` descarcă de asemenea modelul la prima utilizare, dacă acesta nu este deja prezent, apoi îl încarcă pentru inferență.

Modelul apare în lista de modele descărcate a serverului Lemonade odată ce descărcarea este finalizată; verificările de mai jos confirmă că este prezent pe mașină.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-gpt-oss-20b-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q gpt-oss-20b-mxfp4-GGUF
```
<!-- @test:end -->
<!-- @os:end -->