<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка GPT-OSS 20B для Lemonade

Сервер Lemonade обслуживает модель GPT-OSS 20B MXFP4 GGUF (`gpt-oss-20b-mxfp4-GGUF`). Чтобы загрузить её заранее:

```bash
lemonade pull gpt-oss-20b-mxfp4-GGUF
```

Команда `lemonade run gpt-oss-20b-mxfp4-GGUF` также загружает модель при первом использовании, если она ещё не загружена, а затем подготавливает её для инференса.

Модель появляется в списке загруженных моделей сервера Lemonade сразу после завершения загрузки; приведённые ниже проверки подтверждают, что она присутствует на машине.

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