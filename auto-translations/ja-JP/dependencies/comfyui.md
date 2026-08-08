<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. [download.comfy.org](https://download.comfy.org/windows/nsis/x64) から最新の Windows ComfyUI インストーラーをダウンロードします。
2. ハードウェア構成を選択します: `AMD ROCm` を選択します。
3. ComfyUI のインストール先を選択します: デフォルトのパスまたはお好みのフォルダーを使用します。
4. デスクトップアプリの設定: 推奨バージョンのアプリをご利用いただくため、「Automatic Updates」の選択を解除することをお勧めします。
5. 「Next」を押してインストールを開始します。

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUI をクローンする
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (オプション) 特定のバージョンをチェックアウトする
```bash
git checkout v0.19.2
```

#### ComfyUI の必要要件をインストールする

Python 仮想環境を有効化した状態で、以下を実行します:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **注**: 詳細については [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) を参照してください。

<!-- @os:end -->