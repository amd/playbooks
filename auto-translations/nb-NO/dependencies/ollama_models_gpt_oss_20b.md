<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Nedlasting av GPT-OSS 20B for Ollama

Hent GPT-OSS 20B-modellen til Ollama:

```bash
ollama pull gpt-oss:20b
```

Ollama-serveren må kjøre for at nedlastingen skal lykkes; `ollama serve` starter den hvis den ikke allerede kjører.

Bekreft at modellen er til stede:

```bash
ollama list
```

Du bør se `gpt-oss:20b` i utdataene sammen med størrelsen og datoen for siste endring.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->