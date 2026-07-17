<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 AMD Sync 進行遠端開發

## 概覽

**AMD Sync** 可將您的筆記型電腦變成 AMD Ryzen™ AI Halo 的遠端操控中心。省去手動設定 SSH、金鑰和 IDE 的繁瑣步驟——安裝 AMD Sync 後，即可一鍵存取 Ryzen AI Halo 上的遠端終端機、VS Code、JupyterLab，以及即時 GPU/CPU/記憶體儀表板。

您的本機環境保持熟悉的操作方式；所有指令、筆記本和模型均在 Ryzen AI Halo 上執行。

> **提示**：本頁面將包含 AMDSync 的所有最新更新。

## 您將學到的內容

- 在 Ryzen AI Halo 上啟用 SSH，並從 AMD Sync 連線至該裝置
- 一鍵在 Ryzen AI Halo 上啟動 VS Code、終端機、JupyterLab 及即時監控指標
- 使用 AMD Sync 的受管理專案資料夾來組織遠端工作

---

## 核心概念

AMD Sync 分為兩個部分：**用戶端**（您的筆記型電腦，執行 AMD Sync 應用程式）和**伺服器端**（Ryzen AI Halo，執行 AMD Sync 透過隧道連線的 SSH 伺服器）。您從 AMD Sync 啟動的所有工具——VS Code、終端機、筆記本——均在本機開啟，但實際執行於 Ryzen AI Halo 上。

> **支援的用戶端：** Windows 11 和 Linux。不支援 macOS。

---

## 步驟 1 — 在 Ryzen AI Halo 上啟用 SSH


> **注意：** 在 Windows 上，Ryzen AI Halo 出廠時 SSH 伺服器*預設為關閉*。在 Linux 上，SSH 伺服器*預設為開啟*。

1. 在 Ryzen AI Halo 上，開啟 **AMD Ryzen™ AI Developer Center**。
2. 前往 **Remote** 標籤頁。
3. 將 **SSH Server** 切換為開啟。
4. 記下 **Server Information** 下方顯示的 **IP Address**、**Port** 和 **Username**——您將在 AMD Sync 中貼上這些資訊。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意：** 此為 Windows 版 AMD Developer Center。Linux 版的介面可能有所不同，但具備類似的遠端功能。

> **提示：** AMD Sync 要求輸入該使用者的 **OS 登入密碼**，而非 Developer Center 中的密碼。

---

## 步驟 2 — 在您的用戶端安裝 AMD Sync

AMD Sync 可在 Windows 11 和 Linux 上執行。請下載適合您作業系統的安裝程式，然後依照以下步驟操作。安裝完成後，在 **Get Started** 畫面點擊 **Accept & Install**——AMD Sync 完成後將自動啟動。

### Windows

[下載 AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. 雙擊 `AMDSyncInstaller.exe`。
2. 點擊 **Accept & Install**。

> 若 Windows 防火牆出現提示，請允許 AMD Sync 存取網路，以便透過 SSH 連線至 Ryzen AI Halo。

### Linux

點擊連結下載您偏好的格式：

| 格式 | 下載 | 安裝指令 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意：** Ubuntu App Center 可能會將本機開啟的 `.deb` 標記為*「可能不安全」*。這是所有第三方本機安裝程式的標準警告。若雙擊 `.deb` 失敗，請使用上方的終端機指令。

---

## 步驟 3 — 連線至您的 Ryzen AI Halo

首次啟動時，AMD Sync 會顯示 **Add a Remote Device** 表單。請使用 Developer Center **Remote** 標籤頁中的數值填寫。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 欄位 | 說明 |
|-------|-------|
| **Device Name** *（選填）* | 易於識別的標籤，例如 `Ryzen AI Halo`。預設為 `Device 1`、`Device 2`、… |
| **Hostname or IP** | 來自 Remote 標籤頁 |
| **SSH Port** | 來自 Remote 標籤頁（僅限數字） |
| **Username** | 您在 Ryzen AI Halo 上的 OS 帳戶名稱 |
| **Password** | 您的 OS 登入密碼——輸入時會以遮罩顯示 |

點擊 **Add Device**。短暫的載入畫面後，您將看到 **「Connection Successful」**，並進入主畫面，該畫面位於系統匣中。點擊視窗外部可將其關閉；AMD Sync 會持續在背景執行，隨時可一鍵開啟。

> **若連線失敗，** AMD Sync 會返回表單並保留您已填寫的數值。常見原因包括：Ryzen AI Halo 上的 SSH 未啟用、密碼錯誤，或兩台裝置不在同一網路上。

---

## 步驟 4 — 啟動您的第一個遠端工具

主畫面提供五個一鍵元件——無論用戶端和 Ryzen AI Halo 執行哪種作業系統，均可使用。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 元件 | 功能說明 |
|-----------|--------------|
| **Directory** | 選擇 Ryzen AI Halo 上供 VS Code、終端機和 JupyterLab 開啟的資料夾。預設為受管理的 `Documents/AMD_Sync` 工作區。 |
| **VS Code** | 在本機開啟 VS Code，並透過 SSH 隧道連線至所選資料夾。 |
| **Terminal** | 開啟本機終端機，透過 SSH 連線至 Ryzen AI Halo 上的所選資料夾。 |
| **JupyterLab** | 啟動透過 SSH 連線至 Ryzen AI Halo 的筆記本專案，範圍限定於所選資料夾。 |
| **Live Metrics** | 即時檢視 Ryzen AI Halo 上的 GPU、記憶體和 CPU 使用率。 |

### 試用 VS Code

首次啟動時，建議試用 **VS Code**。

1. 將 **Directory** 保留為預設的 `~/Documents/AMD_Sync`。
2. 點擊 **VS Code**。
3. AMD Sync 會在 Ryzen AI Halo 上建立 `Documents/AMD_Sync/Project_1`，並在本機開啟 VS Code，透過隧道連線至該資料夾。

您現在正在使用本機的 VS Code 設定編輯存放於 Ryzen AI Halo 上的檔案。建立 `helloworld.py`，加入 `print("hello world")`，開啟整合式終端機（`` Ctrl + ` ``），然後執行：

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

狀態列顯示 **SSH: Linux**——這證明您的程式碼正在 Ryzen AI Halo 上執行，而非您的筆記型電腦。

### 試用終端機

點擊 **Terminal**，無需離開鍵盤即可透過 SSH 進入同一資料夾。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

在 Windows 上，預設終端機為 **PowerShell**——如有需要，可從設定選單切換至 **Windows Command Prompt**。在 Linux 上，AMD Sync 使用您的系統預設終端機。

---

## Directory 的運作方式

**Directory** 下拉選單是 AMD Sync 中最重要的控制項——它決定您啟動的每個工具在 Ryzen AI Halo 上的存放位置。

- **`~/Documents/AMD_Sync`（預設）** — 從此處啟動 VS Code 或 JupyterLab 時，系統會自動建立新的專案資料夾（VS Code 為 `Project_1`、`Project_2`、…；JupyterLab 為 `Notebook_Project_1`、`Notebook_Project_2`、…）。
- **現有專案資料夾** — `AMD_Sync` 的任何直接子資料夾（包括您在 Ryzen AI Halo 上手動建立的資料夾）都會出現在下拉選單中。您上次使用的資料夾將成為下次的預設選項。
- **自訂路徑** — 輸入任何絕對路徑以開啟 Ryzen AI Halo 上其他位置的資料夾。AMD Sync 僅會*開啟*該資料夾——不會在 `AMD_Sync` 以外建立資料夾，且自訂路徑不會在工作階段之間儲存。

若自訂路徑無法使用，AMD Sync 會告知原因：語法無效、資料夾不存在，或路徑指向的是檔案。

---

## Live Metrics 與 JupyterLab

- **Live Metrics** — GPU、記憶體和 CPU 使用率的即時儀表板。這是確認遠端訓練任務是否確實使用到硬體的最快方式。
- **JupyterLab** — 透過 SSH 連線至 Ryzen AI Halo 的完整筆記本專案，內建整合式終端機，可在不離開介面的情況下混合使用筆記本儲存格和 shell 指令。

---

## 設定與多裝置管理

**Settings** 選單包含三個標籤頁：

| 標籤頁 | 涵蓋內容 |
|-----|----------------|
| **Devices** | 列出您成功連線過的所有 Ryzen AI Halo。可重新連線、編輯憑證或新增裝置。 |
| **Information** | 提供文件和論壇支援的連結。 |
| **Customize** | 調整應用程式在桌面上的位置、切換終端機類型（僅限 Windows），以及檢查 AMD Sync 更新。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **終端機類型（Windows）** — 可在 **PowerShell**（預設）和 **Windows Command Prompt** 之間選擇。
- **終端機類型（Linux）** — 僅可使用系統預設終端機。
- **應用程式更新** — 此標籤頁是在介面內檢查並安裝新版 AMD Sync 的正確位置；無需另外使用更新程式。

> 裝置只有在首次成功連線後才會出現在 **Devices** 下方，因此失敗的嘗試不會造成清單雜亂。

---

## 疑難排解

- **連線立即失敗** — 確認 Ryzen AI Halo 的 Developer Center **Remote** 標籤頁中已啟用 SSH 伺服器。
- **密碼錯誤** — 請使用 Ryzen AI Halo 上的 **OS 登入密碼**，而非 Developer Center 中的密碼。
- **VS Code 按鈕無反應** — 請從 [code.visualstudio.com](https://code.visualstudio.com) 在您的用戶端機器上安裝 VS Code。
- **AMD Sync 系統匣圖示消失（Linux/GNOME）** — 請安裝並啟用 AppIndicator 擴充功能。
- **`.deb` 無法從檔案管理員開啟** — 請在終端機中使用 `sudo apt install ./AMDSyncInstaller.deb`。

---