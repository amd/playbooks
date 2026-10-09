<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

Instalacija Ollama

Pokrenite zvanični instalacioni skript:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Proverite instalaciju:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->