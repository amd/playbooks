<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation von Ollama

Führen Sie das offizielle Installationsskript aus:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Überprüfen Sie die Installation:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->