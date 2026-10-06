<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### הורדת GPT-OSS 20B עבור Ollama

יש למשוך (pull) את מודל GPT-OSS 20B אל תוך Ollama:

```bash
ollama pull gpt-oss:20b
```

שרת Ollama חייב לפעול כדי שהמשיכה (pull) תצליח; הפקודה `ollama serve` מפעילה אותו אם הוא עדיין אינו פועל.

יש לוודא שהמודל קיים:

```bash
ollama list
```

אמורה להופיע `gpt-oss:20b` בפלט, יחד עם גודלו ותאריך העדכון האחרון שלו.

<!-- @os:linux -->
<!-- @test:id=ollama-model-present-gpt-oss-20b-linux timeout=120 hidden=True -->
```bash
ollama list | grep -q 'gpt-oss:20b'
```
<!-- @test:end -->
<!-- @os:end -->