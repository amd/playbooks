<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Lemonade のインストール

<!-- @os:windows -->
最新のインストーラーを [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) からダウンロードし、`.msi` ファイルを実行してください。

インストール後:
- `lemonade` CLI はシステムの PATH に自動的に追加されます
- Lemonade サーバーはバックグラウンドで自動的に実行されることが期待されます

コマンドラインからサイレントインストールすることもできます:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

他のディストリビューションの場合やソースからインストールする場合は、[完全なインストールオプション](https://lemonade-server.ai/docs/guide/install/)を参照してください。
<!-- @os:end -->


#### Lemonade インストールの確認

ターミナルを開いて次のコマンドを実行してください:
```bash
lemonade --version
```

次のような出力が表示されるはずです:
```
lemonade version x.y.z
```

バージョン番号が表示されれば、Lemonade は正しくインストールされており、使用する準備ができています。

クイックリファレンスとして、よく使用される Lemonade CLI コマンドを以下に示します:

| コマンド | 機能 |
| --- | --- |
| `lemonade --help` | 利用可能なすべてのコマンドとフラグを表示します。 |
| `lemonade --version` | インストールされている Lemonade のバージョンを表示します。 |
| `lemonade status` | Lemonade サーバーが実行中でアクセス可能かどうかを確認します。デフォルトの OpenAI 互換 API ベース URL は `http://localhost:13305/api/v1` です。 |
| `lemonade list` | Lemonade セットアップで利用可能なモデルを一覧表示します。 |
| `lemonade pull <MODEL_NAME>` | モデルを起動せずにダウンロードします。 |
| `lemonade run <MODEL_NAME>` | 必要に応じてモデルをダウンロードし、推論/チャット用に起動します。 |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | ROCm バックエンドで llama.cpp モデルを起動します。 |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Vulkan バックエンドで llama.cpp モデルを起動します。 |
| `lemonade config` | 現在の Lemonade 設定値を表示します。 |
| `lemonade config set llamacpp.backend=rocm` | デフォルトの llama.cpp バックエンドを ROCm に設定します。 |

最新の Lemonade サーバーオプションやトラブルシューティングについては、[Lemonade 公式ドキュメント](https://lemonade-server.ai/docs/lemonade-cli/)を参照してください。