<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση του Ollama

Εκτελέστε το επίσημο σενάριο εγκατάστασης:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Επαληθεύστε την εγκατάσταση:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->