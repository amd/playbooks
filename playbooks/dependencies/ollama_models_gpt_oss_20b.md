<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Downloading GPT-OSS 20B for Ollama

Pull the GPT-OSS 20B model into Ollama:

```bash
ollama pull gpt-oss:20b
```

The Ollama server must be running for the pull to succeed; `ollama serve` starts it if it is not already running.

Confirm the model is present:

```bash
ollama list
```

You should see `gpt-oss:20b` in the output along with its size and last-modified date.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->
