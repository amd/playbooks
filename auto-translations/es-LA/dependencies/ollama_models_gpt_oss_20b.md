<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descargando GPT-OSS 20B para Ollama

Descarga el modelo GPT-OSS 20B en Ollama:

```bash
ollama pull gpt-oss:20b
```

El servidor de Ollama debe estar en ejecución para que la descarga se complete correctamente; `ollama serve` lo inicia si aún no está en ejecución.

Confirma que el modelo esté presente:

```bash
ollama list
```

Deberías ver `gpt-oss:20b` en la salida junto con su tamaño y fecha de última modificación.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->