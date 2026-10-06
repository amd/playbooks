<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### OpenClaw のインストール

公式インストーラーを使用して OpenClaw をインストールします。

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-prompt --no-onboard
```

`--no-prompt --no-onboard` フラグは、対話形式のセットアップウィザードをスキップします。これは無人インストールに必要な設定であり、モデルバックエンドは別途設定します。

> **ヒント:** インストール後に `command not found` と表示される場合は、npm のグローバル bin ディレクトリを PATH に追加してください。
> ```bash
> export PATH="$HOME/.npm-global/bin:$PATH"
> ```
> これを恒久的に設定するには、上記の行を `~/.bashrc` または `~/.zshrc` ファイルに追加してください。

<!-- @os:linux -->
<!-- @test:id=openclaw-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.npm-global/bin:$HOME/.local/bin:$PATH"
openclaw --version
```
<!-- @test:end -->
<!-- @os:end -->