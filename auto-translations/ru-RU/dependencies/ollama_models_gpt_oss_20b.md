<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка GPT-OSS 20B для Ollama

Загрузите модель GPT-OSS 20B в Ollama:

```bash
ollama pull gpt-oss:20b
```

Сервер Ollama должен быть запущен для успешной загрузки; `ollama serve` запускает его, если он ещё не запущен.

Убедитесь, что модель присутствует:

```bash
ollama list
```

В выводе вы должны увидеть `gpt-oss:20b` вместе с её размером и датой последнего изменения.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->