<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4-cockpit のインストール

[ds4-cockpit](https://github.com/kyuz0/strix-halo-ds4-toolbox) は、toolbox コンテナの作成、モデルウェイトのダウンロード、サーバーの起動を行う軽量なターミナル UI です。`pipx` を使ってインストールします。

```bash
pipx install "git+https://github.com/kyuz0/strix-halo-ds4-toolbox.git#subdirectory=ds4-strix-halo-cockpit"
```

`pipx` はエントリーポイントを `~/.local/bin` にインストールします。そのディレクトリが `PATH` に含まれていることを確認してください。

<!-- @os:linux -->
<!-- @test:id=ds4-cockpit-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
command -v ds4-cockpit
```
<!-- @test:end -->
<!-- @os:end -->