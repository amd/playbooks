<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. 最新のWindows ComfyUIインストーラーを[download.comfy.org](https://download.comfy.org/windows/nsis/x64)からダウンロードします。
2. ハードウェアのセットアップを選択します：`AMD ROCm`を選択してください。
3. ComfyUIのインストール先を選択します：デフォルトのパスまたはお好みのフォルダーを使用してください。
4. デスクトップアプリの設定：推奨バージョンのアプリを使用していることを確認するため、「Automatic Updates」の選択を解除することをお勧めします。
5. 「Next」を押してインストールを開始します。

<!-- @os:end -->

<!-- @os:linux -->
#### ComfyUIをクローンする
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### （オプション）特定のバージョンをチェックアウトする
```bash
git checkout v0.19.2
```

#### ComfyUIの要件をインストールする

Pythonの仮想環境を有効化した状態で、次のコマンドを実行します：
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **注意**：詳細については[ComfyUI GitHub](https://github.com/comfy-org/ComfyUI)を参照してください。

<!-- @os:end -->