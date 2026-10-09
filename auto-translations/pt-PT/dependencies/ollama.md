<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalar o Ollama

Execute o script de instalação oficial:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verifique a instalação:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->