<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Ollama のインストール

公式インストールスクリプトを実行します。

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

インストールを確認します。

<!-- @os:linux -->
<!-- @test:id=ollama-installed-linux timeout=60 hidden=True -->
```bash
ollama --version
```
<!-- @test:end -->
<!-- @os:end -->