<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下載 GPT-OSS 120B

若要下載 GPT-OSS 120B 模型：

1. 按下鍵盤上的「Ctrl」+「Shift」+「M」，或點擊左側側邊欄的「Discover」標籤（放大鏡圖示）
2. 搜尋 `ggml-org/gpt-oss-120b-GGUF`
3. 選擇 `mxfp4` 並點擊下載

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download.png" alt="LM Studio Download Models" width="600"/>

LM Studio 將自動下載模型並將其放置於正確的目錄中。

若您希望下載其他模型，可在 Discover 標籤中搜尋，LM Studio 將會處理其餘的步驟。

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