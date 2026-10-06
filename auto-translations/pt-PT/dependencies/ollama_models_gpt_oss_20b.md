<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Transferir o GPT-OSS 20B para o Ollama

Obtenha o modelo GPT-OSS 20B no Ollama:

```bash
ollama pull gpt-oss:20b
```

O servidor Ollama tem de estar em execução para que a obtenção seja bem-sucedida; `ollama serve` inicia-o caso ainda não esteja em execução.

Confirme que o modelo está presente:

```bash
ollama list
```

Deverá ver `gpt-oss:20b` no resultado, juntamente com o respetivo tamanho e data da última modificação.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->