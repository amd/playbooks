<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження GPT-OSS 20B для Ollama

Завантажте модель GPT-OSS 20B в Ollama:

```bash
ollama pull gpt-oss:20b
```

Для успішного завантаження сервер Ollama має бути запущений; `ollama serve` запускає його, якщо він ще не запущений.

Переконайтеся, що модель наявна:

```bash
ollama list
```

У виведенні ви маєте побачити `gpt-oss:20b` разом із її розміром та датою останньої зміни.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->