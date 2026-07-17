<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## 先決條件

AMD Ryzen™ AI Halo 開發者平台已預先安裝支援 ROCm 的 PyTorch。對於所有其他裝置，使用者必須手動安裝支援 ROCm 的 PyTorch。請參閱適用於您作業系統的相關章節：

### Windows

| 元件          | 版本            | 備註                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 或更新版本  | AMD Ryzen AI Halo 開發者平台已預先安裝；所有其他裝置必須手動安裝 |

### Linux

| 元件          | 版本            | 備註                              |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 或更新版本  | AMD Ryzen AI Halo 開發者平台已預先安裝；所有其他裝置必須手動安裝 |

## 所需模型

以下模型已針對您的平台進行測試與最佳化：

| 模型 | 參數量 | 大小 | 下載位置 |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | AMD Ryzen AI Halo 開發者平台已預先安裝；所有其他裝置必須手動安裝 |

模型將自動下載至 Hugging Face 快取目錄：
- **Windows**：`C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**：`~/.cache/huggingface/hub/`

請確保模型儲存空間至少有 **50GB 可用空間**。

## 網路需求

初始設定需要網際網路連線以從 Hugging Face 下載模型。下載完成後，playbook 可離線執行。

- 首次模型下載可能需要 **5 至 10 分鐘**，視模型大小與連線速度而定
- 模型會快取至本機，無需重複下載