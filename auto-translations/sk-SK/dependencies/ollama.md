<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Inštalácia Ollama

Spustite oficiálny inštalačný skript:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Overte inštaláciu:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->