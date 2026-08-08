<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下載 GPT-OSS 120B

若要下載 GPT-OSS 120B 模型：

1. 在鍵盤上按下「Ctrl」+「Shift」+「M」，或點選左側邊欄的「Discover」分頁（放大鏡圖示）
2. 搜尋 `ggml-org/gpt-oss-120b-GGUF`
3. 選擇 `mxfp4` 並點選 Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio 會自動下載模型並將其放置於正確的目錄中。

若您想下載其他模型，可以在 Discover 分頁中搜尋，LM Studio 會處理其餘的工作。

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