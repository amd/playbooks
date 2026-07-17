<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# 平台配置

本文件說明執行此 playbook 的預期平台配置。

## 必要應用程式/框架

### Windows/Linux
Lemonade 應預先從[此處](https://lemonade-server.ai/install_options.html)安裝。

- **Open WebUI**（前端網頁應用程式）
- **Lemonade Server**（後端模型伺服器）

> 此 playbook **原生**執行 **Lemonade**（Lemonade server/app）。**Open WebUI** 在 Linux 上以**容器**方式執行（透過 Podman），在 Windows 上則以 **Python 套件**方式執行。`open-webui` PyPI 套件僅支援 Python ≤ 3.12，因此 Linux 容器可避免管理舊版 Python 的問題。

## 模型（在 Lemonade 中）

模型應在 **Lemonade 應用程式**內下載（使用內建的 Model Manager），或透過 Lemonade 的模型管理指令（`lemonade pull <model_name>`）下載。此 playbook 假設以下推薦模型已下載，並顯示於模型清單端點中。

確認模型可用性：
- 開啟：`http://localhost:13305/api/v1/models`
- 已下載的模型將列於 `"data"` 之下。

### 推薦模型

| 功能 | 模型 ID | 備註 |
|---|----|-----|
| LLM（文字輸入 → 文字輸出） | `Qwen3-4B-Hybrid`（或類似模型） | 任何適用於聊天、文字補全、程式撰寫或推理的 Lemonade LLM 模型 |
| VLM（圖像 → 文字） | `Qwen3.5-4B-GGUF`（或 **Vision** 類別中的任何模型） | 任何可將圖像作為輸入的多模態/視覺能力模型 |
| 圖像生成（文字 → 圖像） | `SDXL-Turbo`（或 **Image** 類別中的任何模型） | 任何可根據文字提示生成圖像的 Stable Diffusion 模型 |
| 音訊（語音 → 文字） | `Whisper-Large-v3`（或 **Audio** 類別中的任何模型） | 任何可將音訊轉換為文字的 ASR 模型 |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 使用的連接埠

- **Lemonade Server：** `http://localhost:13305`
- **Open WebUI：** `http://localhost:8080`

若這些連接埠在您的系統上已被佔用，請在啟動伺服器時變更它們。