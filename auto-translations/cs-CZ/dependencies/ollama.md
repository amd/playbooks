<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalace Ollama

Spusťte oficiální instalační skript:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ověřte instalaci:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->