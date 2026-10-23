<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下載 GPT-OSS 120B

<!-- @device:halo_box -->
> **注意：** 如果 LM Studio 中已有此模型，您可以跳過此章節。否則，請依照以下步驟進行下載。
<!-- @device:end -->

若要下載 GPT-OSS 120B 模型：

1. 在鍵盤上按下「Ctrl」+「Shift」+「M」，或點選左側側邊欄的「Discover」分頁（放大鏡圖示）
2. 搜尋 `ggml-org/gpt-oss-120b-GGUF`
3. 選擇 `mxfp4` 並點選 Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio 會自動下載並將模型放置於正確的目錄中。

如果您想下載其他模型，可以在 Discover 分頁中搜尋，LM Studio 會處理其餘的流程。

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