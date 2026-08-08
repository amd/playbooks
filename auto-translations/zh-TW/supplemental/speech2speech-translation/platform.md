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

支援 ROCm 的 PyTorch 已預先安裝於 AMD Ryzen™ AI Halo Developer Platform 上。對於其他所有裝置，使用者必須手動安裝支援 ROCm 的 PyTorch。請參閱您作業系統的相關章節：

### Windows

| 元件          | 版本            | 備註                               |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本  | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；其他所有裝置皆須手動安裝 |

### Linux

| 元件          | 版本            | 備註                               |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本  | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；其他所有裝置皆須手動安裝 |

## 所需模型

以下模型已針對您的平台進行測試與最佳化：

| 模型 | 參數量 | 大小 | 下載位置 |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；其他所有裝置皆須手動安裝 |

模型將自動下載至 Hugging Face 快取目錄：
- **Windows**: `C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**: `~/.cache/huggingface/hub/`

請確保至少有 **20GB 的可用空間** 用於模型儲存。

## 網路需求

初始設定需要網際網路連線，以便從 Hugging Face 下載模型。下載完成後，此 playbook 即可離線執行。

- 首次下載模型視模型大小與連線速度，可能需要 **5-10 分鐘**
- 模型會在本機快取，不需要重新下載