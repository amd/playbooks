<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installazione di Ollama

Esegui lo script di installazione ufficiale:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verifica l'installazione:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->