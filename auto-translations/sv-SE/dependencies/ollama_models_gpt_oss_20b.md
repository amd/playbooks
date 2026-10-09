<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ladda ner GPT-OSS 20B för Ollama

Hämta modellen GPT-OSS 20B till Ollama:

```bash
ollama pull gpt-oss:20b
```

Ollama-servern måste köras för att hämtningen ska lyckas; `ollama serve` startar den om den inte redan körs.

Bekräfta att modellen finns:

```bash
ollama list
```

Du bör se `gpt-oss:20b` i utdata tillsammans med dess storlek och senaste ändringsdatum.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->