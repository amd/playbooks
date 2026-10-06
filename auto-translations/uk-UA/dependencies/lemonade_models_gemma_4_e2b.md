<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження Gemma-4 E2B для Lemonade

Сервер Lemonade обслуговує модель Gemma-4 E2B (`Gemma-4-E2B-it-GGUF`). Щоб завантажити її заздалегідь:

```bash
lemonade pull Gemma-4-E2B-it-GGUF
```

`lemonade run Gemma-4-E2B-it-GGUF` також завантажує модель під час першого використання, якщо її ще немає, а потім завантажує її для виконання висновків.

Модель з'являється у списку завантажених моделей сервера Lemonade після завершення завантаження; наведені нижче перевірки підтверджують її наявність на машині.

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