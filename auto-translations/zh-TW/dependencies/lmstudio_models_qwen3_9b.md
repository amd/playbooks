<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下載 Qwen3.5 9B

若要下載 Qwen3.5 9B 模型：

1. 在鍵盤上按下「Ctrl」+「Shift」+「M」，或點選左側邊欄的「Discover」分頁（放大鏡圖示）
2. 搜尋 `Qwen3.5 9B`
3. 選擇量化版本（建議使用的 `Q4_K_M` 在大小與品質之間取得良好平衡），然後點選下載

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio 會自動下載該模型並將其放置在正確的目錄中。

如果您想下載其他模型，可以在 Discover 分頁中搜尋，LM Studio 會自動處理其餘工作。

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