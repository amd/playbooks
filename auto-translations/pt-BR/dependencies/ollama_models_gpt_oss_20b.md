<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Baixando o GPT-OSS 20B para o Ollama

Baixe o modelo GPT-OSS 20B no Ollama:

```bash
ollama pull gpt-oss:20b
```

O servidor Ollama precisa estar em execução para que o download seja concluído com sucesso; `ollama serve` o inicia caso ainda não esteja em execução.

Confirme se o modelo está presente:

```bash
ollama list
```

Você deve ver `gpt-oss:20b` na saída, junto com seu tamanho e data da última modificação.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->