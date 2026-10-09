<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Het GPT-OSS 20B-model downloaden voor Ollama

Haal het GPT-OSS 20B-model op in Ollama:

```bash
ollama pull gpt-oss:20b
```

De Ollama-server moet actief zijn om het ophalen te laten slagen; `ollama serve` start de server als deze nog niet actief is.

Bevestig dat het model aanwezig is:

```bash
ollama list
```

U zou `gpt-oss:20b` in de uitvoer moeten zien, samen met de bestandsgrootte en de datum van de laatste wijziging.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->