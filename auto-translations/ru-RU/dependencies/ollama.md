<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка Ollama

Запустите официальный скрипт установки:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Проверьте установку:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->