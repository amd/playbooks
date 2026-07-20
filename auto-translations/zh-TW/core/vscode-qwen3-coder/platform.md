<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 所需的預期平台配置。

## Windows

### LM Studio 安裝

LM Studio 應已預先安裝：

| 元件 | 版本 | 位置 |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### 模型下載

以下模型應已存在於 LM Studio 的模型目錄中（`C:\Users\...\.lmstudio\models`）：

| 模型類型 | 量化 | 大小 | 位置 |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### LM Studio 安裝

請參閱 lmstudio.md（位於 dependencies 資料夾中）以取得更多詳細資訊。

### 模型下載

與 Windows 相同。