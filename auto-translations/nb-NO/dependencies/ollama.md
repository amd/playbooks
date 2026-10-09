<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installere Ollama

Kjør det offisielle installasjonsskriptet:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Bekreft installasjonen:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->