<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stahování GPT-OSS 20B pro Ollama

Stáhněte model GPT-OSS 20B do Ollama:

```bash
ollama pull gpt-oss:20b
```

Aby stahování proběhlo úspěšně, musí běžet server Ollama; pokud ještě neběží, spustí ho příkaz `ollama serve`.

Ověřte, že je model k dispozici:

```bash
ollama list
```

Ve výstupu byste měli vidět `gpt-oss:20b` společně s jeho velikostí a datem poslední úpravy.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->