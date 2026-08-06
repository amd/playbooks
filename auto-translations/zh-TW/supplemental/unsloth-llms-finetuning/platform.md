<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台設定

本文件說明執行此 playbook 所需的平台設定。

## 先決條件

具備 ROCm 支援的 PyTorch 已預先安裝在 AMD Ryzen™ AI Halo Developer Platform 上。對於其他所有裝置，使用者必須手動安裝具備 ROCm 支援的 PyTorch。請參閱您作業系統對應的章節：


### Windows

| 元件     | 版本         | 備註                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13  | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；其他所有裝置皆須手動安裝 |


### Linux

| 元件     | 版本         | 備註                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.11.x + ROCm 7.13   | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；其他所有裝置皆須手動安裝 |


## 必要模型

以下模型已針對您的平台進行測試並最佳化：

| 模型 | 參數 | 大小 | 下載位置 |
|-------|------------|------|-------------------|
| **unsloth/gemma-4-E4B-it** | 8B | ~16GB | 從 HF 下載

模型將自動下載至 Hugging Face 快取目錄：`~/.cache/huggingface/hub/`

請確保至少有 **20GB 的可用空間** 用於模型儲存。

## 網路需求

初次設定需要網路連線，以便從 Hugging Face 下載模型。下載完成後，此 playbook 即可離線執行。

- 首次下載模型可能需要 **5-10 分鐘**，視模型大小與網路連線速度而定
- 模型會在本機快取，不需重複下載