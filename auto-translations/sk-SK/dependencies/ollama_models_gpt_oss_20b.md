<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie GPT-OSS 20B pre Ollama

Stiahnite model GPT-OSS 20B do Ollamy:

```bash
ollama pull gpt-oss:20b
```

Server Ollama musí bežať, aby sa sťahovanie podarilo; príkaz `ollama serve` ho spustí, ak ešte nebeží.

Overte, že je model prítomný:

```bash
ollama list
```

Vo výstupe by ste mali vidieť `gpt-oss:20b` spolu s jeho veľkosťou a dátumom poslednej zmeny.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->