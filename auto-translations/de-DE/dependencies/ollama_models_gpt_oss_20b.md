<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Herunterladen von GPT-OSS 20B für Ollama

Laden Sie das GPT-OSS 20B-Modell in Ollama herunter:

```bash
ollama pull gpt-oss:20b
```

Der Ollama-Server muss laufen, damit der Download erfolgreich ist; `ollama serve` startet ihn, falls er noch nicht läuft.

Bestätigen Sie, dass das Modell vorhanden ist:

```bash
ollama list
```

Sie sollten `gpt-oss:20b` in der Ausgabe zusammen mit seiner Größe und dem Datum der letzten Änderung sehen.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->