<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การติดตั้ง Ollama

เรียกใช้สคริปต์การติดตั้งอย่างเป็นทางการ:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

ตรวจสอบการติดตั้ง:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->