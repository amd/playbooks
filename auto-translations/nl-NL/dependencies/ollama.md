<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama installeren

Voer het officiële installatiescript uit:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Controleer de installatie:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->