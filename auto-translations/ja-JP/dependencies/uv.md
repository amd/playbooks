<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### uv のインストール

[uv](https://docs.astral.sh/uv/) は、Agent Canvas がエージェントサーバー環境を構築するために使用する Python のパッケージ/環境マネージャーです。公式スクリプトでインストールしてください。

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` は `~/.local/bin` にインストールされます。そのディレクトリが `PATH` に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->