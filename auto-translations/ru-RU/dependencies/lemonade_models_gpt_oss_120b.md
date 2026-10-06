<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка GPT-OSS 120B для Lemonade

Сервер Lemonade обслуживает модель GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Чтобы загрузить её заранее:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

Команда `lemonade run gpt-oss-120b-mxfp-GGUF` также загружает модель при первом использовании, если она ещё не присутствует на машине, а затем загружает её для вывода.

Модель появится в списке загруженных моделей сервера Lemonade после завершения загрузки; приведённые ниже проверки подтверждают, что она присутствует на машине.

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