<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio での GPT-OSS 120B のダウンロード

<!-- @device:halo_box -->
> **注:** このモデルがすでに LM Studio で利用可能な場合は、このセクションをスキップできます。そうでない場合は、以下の手順に従ってダウンロードしてください。
<!-- @device:end -->

GPT-OSS 120B モデルをダウンロードするには:

1. キーボードで "Ctrl" + "Shift" + "M" を押すか、左サイドバーの "Discover" タブ(虫眼鏡アイコン)をクリックします
2. `ggml-org/gpt-oss-120b-GGUF` を検索します
3. `mxfp4` を選択して Download をクリックします

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio が自動的にモデルをダウンロードし、正しいディレクトリに配置します。

他のモデルをダウンロードしたい場合は、Discover タブで検索すれば、LM Studio が残りを処理します。

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "gpt-oss-120b"
```
<!-- @test:end -->
<!-- @os:end -->