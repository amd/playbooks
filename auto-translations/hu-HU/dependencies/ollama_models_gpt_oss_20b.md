<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GPT-OSS 20B letöltése Ollamához

Töltsd le a GPT-OSS 20B modellt Ollamába:

```bash
ollama pull gpt-oss:20b
```

A letöltés sikeréhez az Ollama szervernek futnia kell; a `ollama serve` elindítja, ha még nem fut.

Erősítsd meg, hogy a modell elérhető:

```bash
ollama list
```

A kimenetben meg kell jelennie a `gpt-oss:20b` bejegyzésnek, a méretével és az utolsó módosítás dátumával együtt.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->