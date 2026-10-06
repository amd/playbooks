<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descărcarea GPT-OSS 20B pentru Ollama

Descărcați modelul GPT-OSS 20B în Ollama:

```bash
ollama pull gpt-oss:20b
```

Serverul Ollama trebuie să ruleze pentru ca descărcarea să reușească; `ollama serve` îl pornește dacă nu rulează deja.

Confirmați că modelul este prezent:

```bash
ollama list
```

Ar trebui să vedeți `gpt-oss:20b` în rezultat, împreună cu dimensiunea și data ultimei modificări.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->