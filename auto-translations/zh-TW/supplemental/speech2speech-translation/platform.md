# 平台配置

本文件說明執行此 playbook 所需的平台配置。

## 先決條件

支援 ROCm 的 PyTorch 已預先安裝於 AMD Ryzen™ AI Halo Developer Platform。對於所有其他裝置，使用者必須手動安裝支援 ROCm 的 PyTorch。請參閱您作業系統對應的章節：

### Windows

| 元件     | 版本         | 備註                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本    | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；所有其他裝置必須手動安裝 |

### Linux

| 元件     | 版本         | 備註                             |
|---------------|-----------------|-----------------------------------|
| **PyTorch**   | 2.8 或更新版本    | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；所有其他裝置必須手動安裝 |

## 必要模型

以下模型已經過測試並針對您的平台進行最佳化：

| 模型 | 參數 | 大小 | 下載位置 |
|-------|------------|------|-------------------|
| **facebook/seamless-m4t-v2-large** | 2.3B | ~10GB | 已預先安裝於 AMD Ryzen AI Halo Developer Platform；所有其他裝置必須手動安裝 |

模型將自動下載至 Hugging Face 快取目錄：
- **Windows**：`C:\Users\<username>\.cache\huggingface\hub\`
- **Linux**：`~/.cache/huggingface/hub/`

請確保至少有 **20GB 可用空間**用於模型儲存。

## 網路需求

初始設定需要網際網路連線以從 Hugging Face 下載模型。下載完成後，此 playbook 即可離線執行。

- 首次下載模型可能需要 **5-10 分鐘**，視模型大小與連線速度而定
- 模型會快取於本機，無需重新下載