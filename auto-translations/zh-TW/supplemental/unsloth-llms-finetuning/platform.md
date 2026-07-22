<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

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