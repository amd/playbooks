<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalando Ollama

Ejecuta el script de instalación oficial:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Verifica la instalación:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->