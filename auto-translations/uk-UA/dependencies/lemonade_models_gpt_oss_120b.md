<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження GPT-OSS 120B для Lemonade

Сервер Lemonade обслуговує модель GPT-OSS 120B MXFP4 GGUF (`gpt-oss-120b-mxfp-GGUF`). Щоб завантажити її заздалегідь:

```bash
lemonade pull gpt-oss-120b-mxfp-GGUF
```

`lemonade run gpt-oss-120b-mxfp-GGUF` також завантажує модель під час першого використання, якщо її ще немає, а потім завантажує її для виконання висновків.

Модель з’являється у списку завантажених моделей сервера Lemonade після завершення завантаження; перевірки нижче підтверджують її наявність на машині.

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