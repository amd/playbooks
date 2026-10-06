<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hermes のインストール

公式インストーラーを使用して Hermes エージェント CLI をインストールします。`--skip-setup` フラグを指定すると、無人でインストールを行うことができます。

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup
```

Hermes は `~/.local/bin` にインストールされます。このディレクトリが `PATH` に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=hermes-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
hermes --version
```
<!-- @test:end -->
<!-- @os:end -->