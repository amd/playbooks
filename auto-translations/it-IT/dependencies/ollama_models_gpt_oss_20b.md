<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Scaricare GPT-OSS 20B per Ollama

Scarica il modello GPT-OSS 20B in Ollama:

```bash
ollama pull gpt-oss:20b
```

Il server Ollama deve essere in esecuzione affinché il download abbia successo; `ollama serve` lo avvia se non è già in esecuzione.

Conferma che il modello sia presente:

```bash
ollama list
```

Dovresti vedere `gpt-oss:20b` nell'output insieme alla sua dimensione e alla data dell'ultima modifica.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->