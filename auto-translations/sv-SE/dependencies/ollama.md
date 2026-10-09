<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installera Ollama

Kör det officiella installationsskriptet:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verifiera installationen:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->