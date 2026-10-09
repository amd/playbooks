<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка Qwen3 4B Hybrid для Lemonade

Сервер Lemonade обслуживает модель Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), которая работает на NPU и GPU процессоров Ryzen AI. Чтобы загрузить её заранее:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Модель появится в списке загруженных моделей сервера Lemonade после завершения загрузки; приведённая ниже проверка подтверждает её наличие на машине.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->