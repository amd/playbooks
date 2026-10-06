<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка Qwen3.5 4B для Lemonade

Сервер Lemonade обслуживает модель Qwen3.5 4B (`Qwen3.5-4B-GGUF`). Чтобы загрузить её заранее:

```bash
lemonade pull Qwen3.5-4B-GGUF
```

Команда `lemonade run Qwen3.5-4B-GGUF` также загружает модель при первом использовании, если она ещё не присутствует, а затем загружает её для вывода.

Модель появляется в списке загруженных моделей сервера Lemonade после завершения загрузки; приведённые ниже проверки подтверждают, что она присутствует на машине.

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