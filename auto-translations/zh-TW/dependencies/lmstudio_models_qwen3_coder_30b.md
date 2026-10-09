<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 在 LM Studio 上下載 Qwen3-Coder 30B

若要下載 Qwen3-Coder 30B 模型：

1. 在鍵盤上按下「Ctrl」+「Shift」+「M」，或點選左側邊欄的「Discover」分頁（放大鏡圖示）
2. 搜尋 `Qwen3-Coder-30B-A3B`
3. 選擇量化版本（建議使用 `Q4_K_M`，可在大小與品質之間取得良好平衡），然後點選下載

LM Studio 將自動下載模型並將其放置在正確的目錄中。

若您想下載其他模型，可以在 Discover 分頁中搜尋，LM Studio 會處理其餘的下載作業。

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