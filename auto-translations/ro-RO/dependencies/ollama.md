<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalarea Ollama

Rulați scriptul oficial de instalare:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verificați instalarea:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->