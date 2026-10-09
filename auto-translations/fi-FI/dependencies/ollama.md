<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollaman asentaminen

Suorita virallinen asennusskripti:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Varmista asennus:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->