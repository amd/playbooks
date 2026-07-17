<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下載 Qwen3.5 9B

若要下載 Qwen3.5 9B 模型：

1. 按下鍵盤上的 "Ctrl" + "Shift" + "M"，或點擊左側側邊欄的「探索」標籤（放大鏡圖示）
2. 搜尋 `Qwen3.5 9B`
3. 選擇量化版本（建議使用 `Q4_K_M`，在大小與品質之間取得良好平衡），然後點擊下載

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio 將自動下載模型並將其放置於正確的目錄中。

若您希望下載其他模型，可在探索標籤中搜尋，LM Studio 將會處理其餘的步驟。

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