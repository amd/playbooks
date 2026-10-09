<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama telepítése

Futtassa a hivatalos telepítő szkriptet:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Ellenőrizze a telepítést:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->