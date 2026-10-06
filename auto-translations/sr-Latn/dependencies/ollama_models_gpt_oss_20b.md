<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje GPT-OSS 20B modela za Ollama

Preuzmite GPT-OSS 20B model u Ollama:

```bash
ollama pull gpt-oss:20b
```

Ollama server mora biti pokrenut da bi preuzimanje uspelo; `ollama serve` ga pokreće ako već nije pokrenut.

Potvrdite da je model prisutan:

```bash
ollama list
```

Trebalo bi da vidite `gpt-oss:20b` u izlazu zajedno sa njegovom veličinom i datumom poslednje izmene.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->