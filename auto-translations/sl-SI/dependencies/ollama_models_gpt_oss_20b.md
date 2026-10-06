<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos GPT-OSS 20B za Ollama

Povlecite model GPT-OSS 20B v Ollama:

```bash
ollama pull gpt-oss:20b
```

Strežnik Ollama mora delovati, da je povlek uspešen; `ollama serve` ga zažene, če še ne deluje.

Potrdite, da je model prisoten:

```bash
ollama list
```

V izpisu bi morali videti `gpt-oss:20b` skupaj z njegovo velikostjo in datumom zadnje spremembe.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->