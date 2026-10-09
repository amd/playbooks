<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת GPT-OSS 20B עבור Ollama

משכו את מודל GPT-OSS 20B אל תוך Ollama:

```bash
ollama pull gpt-oss:20b
```

שרת Ollama חייב לפעול כדי שהמשיכה תצליח; `ollama serve` מפעיל אותו אם הוא עדיין לא פועל.

ודאו שהמודל קיים:

```bash
ollama list
```

אמור להופיע `gpt-oss:20b` בפלט, יחד עם גודלו ותאריך העדכון האחרון שלו.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->