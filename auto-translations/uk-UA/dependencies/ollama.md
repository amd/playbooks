<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Встановлення Ollama

Запустіть офіційний скрипт встановлення:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Перевірте встановлення:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->