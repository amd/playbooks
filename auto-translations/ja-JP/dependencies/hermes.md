<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermesのインストール

公式インストーラーを使用してHermesエージェントCLIをインストールします。`--skip-setup`フラグを使用すると、無人でインストールを行うことができます。

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermesは`~/.local/bin`にインストールされます。そのディレクトリが`PATH`に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->