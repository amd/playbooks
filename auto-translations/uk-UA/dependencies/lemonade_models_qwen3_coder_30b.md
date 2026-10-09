<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження Qwen3-Coder 30B A3B для Lemonade

Сервер Lemonade обслуговує модель Qwen3-Coder 30B A3B (`Qwen3-Coder-30B-A3B-Instruct-GGUF`). Щоб завантажити її заздалегідь:

```bash
lemonade pull Qwen3-Coder-30B-A3B-Instruct-GGUF
```

Команда `lemonade run Qwen3-Coder-30B-A3B-Instruct-GGUF` також завантажує модель під час першого використання, якщо її ще немає, а потім завантажує її для інференсу.

Модель з'являється у списку завантажених моделей сервера Lemonade після завершення завантаження; наведені нижче перевірки підтверджують її наявність на машині.

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