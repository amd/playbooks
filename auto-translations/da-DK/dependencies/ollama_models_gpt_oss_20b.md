<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Download af GPT-OSS 20B til Ollama

Hent GPT-OSS 20B-modellen til Ollama:

```bash
ollama pull gpt-oss:20b
```

Ollama-serveren skal køre, for at hentningen kan lykkes; `ollama serve` starter den, hvis den ikke allerede kører.

Bekræft, at modellen er til stede:

```bash
ollama list
```

Du bør se `gpt-oss:20b` i outputtet sammen med dens størrelse og dato for seneste ændring.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->