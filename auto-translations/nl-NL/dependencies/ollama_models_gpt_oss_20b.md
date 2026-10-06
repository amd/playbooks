<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 20B downloaden voor Ollama

Haal het GPT-OSS 20B-model binnen in Ollama:

```bash
ollama pull gpt-oss:20b
```

De Ollama-server moet actief zijn om de pull te laten slagen; `ollama serve` start deze als hij nog niet actief is.

Bevestig dat het model aanwezig is:

```bash
ollama list
```

Je zou `gpt-oss:20b` in de uitvoer moeten zien, samen met de grootte en de datum van laatste wijziging.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->