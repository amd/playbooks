<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台配置

本文件說明執行此 playbook 所需的預期平台配置。

## 先決條件

具備 ROCm 支援的 PyTorch 已預先安裝在 AMD Ryzen™ AI Halo Developer Platform 上。對於所有其他裝置，使用者必須手動安裝具備 ROCm 支援的 PyTorch。請參閱您作業系統對應的章節：

### Windows

| 元件     | 版本         | 備註                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 或更新版本    | 已預先安裝在 AMD Ryzen AI Halo Developer Platform 上；必須在所有其他裝置上手動安裝 |

### Linux

| 元件     | 版本         | 備註                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.9 或更新版本    | 已預先安裝在 AMD Ryzen AI Halo Developer Platform 上；必須在所有其他裝置上手動安裝 |

## 必要模型

以下模型已針對您的平台進行測試與最佳化：

| 模型 | 參數量 | 大小 | 下載位置 |
|-------|------------|------|-------------------|
| **openai/gpt-oss-20b** | 20B | ~40GB | 已預先安裝在 AMD Ryzen AI Halo Developer Platform 上；必須在所有其他裝置上手動安裝 |

模型將自動下載至 Hugging Face 快取目錄：
- **Windows**：`C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**：`~/.cache/huggingface/hub/`

請確保至少有 **50GB 的可用空間** 用於模型儲存。

## 網路需求

初次設定需要網際網路連線以從 Hugging Face 下載模型。下載完成後，此 playbook 便可離線執行。

- 首次下載模型可能需要 **5-10 分鐘**，視模型大小與連線速度而定
- 模型會快取於本機，無需重新下載