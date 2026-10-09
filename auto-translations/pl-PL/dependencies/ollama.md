<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalowanie Ollama

Uruchom oficjalny skrypt instalacyjny:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Zweryfikuj instalację:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->