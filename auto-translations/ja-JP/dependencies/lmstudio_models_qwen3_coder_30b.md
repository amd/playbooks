<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM StudioでQwen3-Coder 30Bをダウンロードする

Qwen3-Coder 30Bモデルをダウンロードするには:

1. キーボードで「Ctrl」+「Shift」+「M」を押すか、左サイドバーの「Discover」タブ(虫眼鏡アイコン)をクリックします
2. `Qwen3-Coder-30B-A3B` を検索します
3. 量子化を選択し(推奨される `Q4_K_M` はサイズと品質のバランスが良好です)、Downloadをクリックします

LM Studioが自動的にモデルをダウンロードし、正しいディレクトリに配置します。

追加のモデルをダウンロードしたい場合は、Discoverタブで検索すれば、LM Studioが残りの処理を行います。

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->