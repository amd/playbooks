<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### uvのインストール

[uv](https://docs.astral.sh/uv/)はAgent Canvasがエージェントサーバー環境を構築する際に使用するPythonパッケージ/環境マネージャーです。公式スクリプトでインストールしてください。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv`は`~/.local/bin`にインストールされます。このディレクトリが`PATH`に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->