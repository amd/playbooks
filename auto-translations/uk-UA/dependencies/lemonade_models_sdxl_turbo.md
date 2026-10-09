<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження SDXL-Turbo для Lemonade

Сервер Lemonade обслуговує модель SDXL-Turbo (`SDXL-Turbo`). Щоб завантажити її заздалегідь:

```bash
lemonade pull SDXL-Turbo
```

`lemonade run SDXL-Turbo` також завантажує модель під час першого використання, якщо вона ще не присутня, а потім завантажує її для виконання висновків.

Модель з'являється у списку завантажених моделей сервера Lemonade одразу після завершення завантаження; наведені нижче перевірки підтверджують її наявність на машині.

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