<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama 설치하기

공식 설치 스크립트를 실행합니다:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

설치를 확인합니다:

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->