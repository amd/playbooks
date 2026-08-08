<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio で Qwen3.5 9B をダウンロードする

Qwen3.5 9B モデルをダウンロードするには:

1. キーボードで "Ctrl" + "Shift" + "M" を押すか、左サイドバーの "Discover" タブ(虫眼鏡アイコン)をクリックします
2. `Qwen3.5 9B` を検索します
3. 量子化を選択し(推奨の `Q4_K_M` はサイズと品質のバランスが良好です)、Download をクリックします

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio が自動的にモデルをダウンロードし、正しいディレクトリに配置します。

追加のモデルをダウンロードしたい場合は、Discover タブで検索すれば、あとは LM Studio が処理してくれます。

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->