<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### התקנת Ollama

הריצו את סקריפט ההתקנה הרשמי:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

אמתו את ההתקנה:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->