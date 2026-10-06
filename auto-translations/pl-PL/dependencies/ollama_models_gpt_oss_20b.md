<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie modelu GPT-OSS 20B dla Ollama

Pobierz model GPT-OSS 20B do Ollama:

```bash
ollama pull gpt-oss:20b
```

Aby pobieranie się powiodło, serwer Ollama musi być uruchomiony; `ollama serve` uruchamia go, jeśli nie działa jeszcze.

Potwierdź, że model jest obecny:

```bash
ollama list
```

W wynikach powinieneś zobaczyć `gpt-oss:20b` wraz z jego rozmiarem i datą ostatniej modyfikacji.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->