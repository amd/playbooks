<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM StudioでGPT-OSS 120Bをダウンロードする

GPT-OSS 120Bモデルをダウンロードするには:

1. キーボードで「Ctrl」+「Shift」+「M」を押すか、左サイドバーの「Discover」タブ（虫眼鏡アイコン）をクリックします
2. `ggml-org/gpt-oss-120b-GGUF` を検索します
3. `mxfp4` を選択し、Downloadをクリックします

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studioは自動的にモデルをダウンロードし、正しいディレクトリに配置します。

他のモデルもダウンロードしたい場合は、Discoverタブで検索するだけで、あとはLM Studioが処理してくれます。

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