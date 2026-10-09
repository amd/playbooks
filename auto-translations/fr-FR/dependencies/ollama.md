<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation d'Ollama

Exécutez le script d'installation officiel :

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Vérifiez l'installation :

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->