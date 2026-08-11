<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

# 平台設定

本文件說明執行此手冊所需的平台設定。

## 必要的應用程式/框架

### Windows/Linux
應從[此處](https://lemonade-server.ai/install_options.html)預先安裝 Lemonade。

- **Open WebUI**（前端網頁應用程式）
- **Lemonade Server**（後端模型伺服器）

> 此手冊以**原生**方式執行 **Lemonade**（Lemonade server/app）。**Open WebUI** 在 Linux 上以**容器**方式執行（透過 Podman），在 Windows 上則以 **Python 套件**方式執行。`open-webui` PyPI 套件僅支援 Python ≤ 3.12，因此 Linux 容器可避免需要管理較舊版本 Python 的問題。

## 模型（於 Lemonade 中）

模型應在 **Lemonade app** 內下載（使用內建的 Model Manager），或透過 Lemonade 的模型管理指令（`lemonade pull <model_name>`）下載。此手冊假設下列建議模型已下載完成，並顯示在模型清單端點中。

檢查模型可用性：
- 開啟：`http://localhost:13305/api/v1/models`
- 已下載的模型會列在 `"data"` 下方。

### 建議模型

| 功能 | 模型 ID | 備註 |
|---|----|-----|
| LLM（文字輸入 → 文字輸出） | `Qwen3-4B-Hybrid`（或類似模型） | 任何可用於聊天、文字補全、程式撰寫或推理的 Lemonade LLM 模型 |
| VLM（圖片 → 文字） | `Qwen3.5-4B-GGUF`（或**Vision**類別中的任何模型） | 任何可將圖片作為輸入一部分的多模態/視覺辨識模型 |
| 圖像生成（文字 → 圖像） | `SDXL-Turbo`（或**Image**類別中的任何模型） | 任何可根據文字提示生成圖像的 Stable Diffusion 模型 |
| 音訊（語音 → 文字） | `Whisper-Large-v3`（或**Audio**類別中的任何模型） | 任何可將音訊轉換為文字的 ASR 模型 |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## 使用的連接埠

- **Lemonade Server：** `http://localhost:13305`
- **Open WebUI：** `http://localhost:8080`

若您的系統上這些連接埠已被使用，請在啟動伺服器時變更它們。