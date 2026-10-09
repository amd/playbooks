<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження Qwen3 4B Hybrid для Lemonade

Сервер Lemonade обслуговує модель Qwen3 4B Hybrid (`Qwen3-4B-Hybrid`), яка працює на NPU та GPU процесорів Ryzen AI. Щоб завантажити її заздалегідь:

```powershell
lemonade pull Qwen3-4B-Hybrid
```

Модель з'явиться у списку завантажених моделей сервера Lemonade після завершення завантаження; наведена нижче перевірка підтверджує її наявність на машині.

<!-- @os:windows -->
<!-- @test:id=lemonade-model-present-qwen3-4b-hybrid-windows timeout=60 hidden=True -->
```powershell
curl.exe -sf --max-time 5 http://127.0.0.1:13305/api/v1/models | findstr /C:Qwen3-4B-Hybrid
```
<!-- @test:end -->
<!-- @os:end -->