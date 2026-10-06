<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### تثبيت Ollama

شغّل سكربت التثبيت الرسمي:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

تحقق من التثبيت:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->