<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка SDXL-Turbo для Lemonade

Сервер Lemonade обслуживает модель SDXL-Turbo (`SDXL-Turbo`). Чтобы загрузить её заранее:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` также загружает модель при первом использовании, если она ещё не присутствует, а затем загружает её для вывода.

Модель появляется в списке загруженных моделей сервера Lemonade после завершения загрузки; приведённые ниже проверки подтверждают, что она присутствует на машине.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lemonade-model-present-sdxl-turbo-linux timeout=60 hidden=True -->
```bash
curl -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | grep -q SDXL-Turbo
```
<!-- @test:end -->
<!-- @os:end -->