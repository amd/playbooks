<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama Kurulumu

Resmi kurulum betiğini çalıştırın:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Kurulumu doğrulayın:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->