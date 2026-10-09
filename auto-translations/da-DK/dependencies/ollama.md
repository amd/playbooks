<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installation af Ollama

Kør det officielle installationsscript:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Bekræft installationen:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->