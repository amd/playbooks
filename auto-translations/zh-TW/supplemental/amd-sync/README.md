<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **機器翻譯。**本頁面是由英文自動翻譯而成，尚未經過人工審閱。內容可能包含錯誤，且某些指示、命令、下載項目、產品供應情況或其他內容可能因語言或地區而異。如本文件與英文版本之間存在任何不一致或差異，應以該 playbook 之英文原始版本為準。
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 AMD Sync 進行遠端開發

## 概述

**AMD Sync** 將您的筆記型電腦變成 AMD Ryzen™ AI Halo 的遠端駕駛艙。跳過手動 SSH、金鑰和 IDE 設定 — 安裝 AMD Sync,即可一鍵存取遠端終端機、VS Code、JupyterLab,以及 Ryzen AI Halo 上即時的 GPU/CPU/記憶體儀表板。

您的本機保持不變;每個指令、筆記本和模型都在 Ryzen AI Halo 上執行。

> **提示**:此頁面將包含 AMDSync 的任何新更新。

## 您將學到

- 在 Ryzen AI Halo 上啟用 SSH,並從 AMD Sync 連線至它
- 一鍵針對 Ryzen AI Halo 啟動 VS Code、終端機、JupyterLab 和即時指標
- 使用 AMD Sync 的受管理專案資料夾組織遠端工作

---

## 核心概念

AMD Sync 有兩端:**用戶端**(您的筆記型電腦,執行 AMD Sync 應用程式)和**伺服器端**(Ryzen AI Halo,執行 AMD Sync 隧道連接的 SSH 伺服器)。您從 AMD Sync 啟動的所有項目 — VS Code、終端機、筆記本 — 都會在本機開啟,但在 Ryzen AI Halo 上執行。

> **支援的用戶端:**Windows 11 和 Linux。不支援 macOS。

---

## 步驟 1 — 在 Ryzen AI Halo 上啟用 SSH


> **注意:**在 Windows 上,Ryzen AI Halo 出廠時 SSH 伺服器*預設為關閉*。在 Linux 上,SSH 伺服器*預設為開啟*。

1. 在 Ryzen AI Halo 上,開啟 **AMD Ryzen™ AI Developer Center**。
2. 前往**「Remote」**分頁。
3. 開啟 **SSH Server** 切換開關。
4. 記下 **Server Information** 下顯示的 **IP Address**、**Port** 和 **Username** — 您稍後將貼到 AMD Sync 中。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意:**這是 Windows 版的 AMD Developer Center。Linux 版的介面可能不同,但具有類似的遠端功能。

> **提示:**AMD Sync 詢問的是該使用者的**作業系統登入密碼**,而不是 Developer Center 的密碼。

---

## 步驟 2 — 在您的用戶端安裝 AMD Sync

AMD Sync 可在 Windows 11 和 Linux 上執行。下載適用於您作業系統的安裝程式,然後依照下列步驟操作。安裝完成後,在 **Get Started** 畫面上按一下 **Accept & Install** — AMD Sync 完成後會自動啟動。

### Windows

[下載 AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. 按兩下 `AMDSyncInstaller.exe`。
2. 按一下 **Accept & Install**。

> 如果 Windows 防火牆跳出提示,請允許 AMD Sync 的網路存取權限,讓它能透過 SSH 連接到 Ryzen AI Halo。

### Linux

按一下連結以下載您偏好的格式:

| 格式 | 下載 | 安裝指令 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意:**Ubuntu App Center 可能會將本機開啟的 `.deb` 標記為*「可能不安全」*。這是任何第三方本機安裝程式的標準警告。如果按兩下 `.deb` 失敗,請使用上方的終端機指令。

---

## 步驟 3 — 連線至您的 Ryzen AI Halo

首次啟動時,AMD Sync 會顯示**「Add a Remote Device」**表單。請使用 Developer Center 的**「Remote」**分頁中的值填寫。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 欄位 | 備註 |
|-------|-------|
| **Device Name**(選填) | 一個好記的名稱,例如 `Ryzen AI Halo`。預設為 `Device 1`、`Device 2`,以此類推 |
| **Hostname or IP** | 來自 Remote 分頁 |
| **SSH Port** | 來自 Remote 分頁(僅限數字) |
| **Username** | 您在 Ryzen AI Halo 上的作業系統帳戶名稱 |
| **Password** | 您的作業系統登入密碼 — 輸入時會遮蔽顯示 |

按一下 **Add Device**。經過短暫的載入畫面後,您將看到**「Connection Successful」**,並進入主畫面,此畫面位於您的系統匣中。點選視窗外的位置即可關閉它;AMD Sync 會持續在背景執行,只需一鍵即可再次開啟。

> **如果連線失敗,**AMD Sync 會返回表單,並保留您輸入的值。常見原因為 Ryzen AI Halo 上停用了 SSH、密碼錯誤,或兩台裝置位於不同的網路上。

---

## 步驟 4 — 啟動您的第一個遠端工具

主畫面提供五個一鍵功能元件 — 無論用戶端與 Ryzen AI Halo 執行哪種作業系統,皆可使用全部功能。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 元件 | 功能說明 |
|-----------|--------------|
| **Directory** | 選擇 VS Code、終端機和 JupyterLab 將在 Ryzen AI Halo 上開啟的資料夾。預設為受管理的 `Documents/AMD_Sync` 工作區。 |
| **VS Code** | 在本機開啟 VS Code,並透過 SSH 隧道連接到所選資料夾。 |
| **Terminal** | 開啟一個本機終端機,透過 SSH 連接到 Ryzen AI Halo,並位於所選資料夾中。 |
| **JupyterLab** | 啟動一個筆記本專案,透過 SSH 連接到 Ryzen AI Halo,範圍限定於所選資料夾。 |
| **Live Metrics** | Ryzen AI Halo 上 GPU、記憶體和 CPU 使用率的即時檢視畫面。 |

### 試用 VS Code

首次啟動時,請試用 **VS Code**。

1. 讓 **Directory** 保持預設值 `~/Documents/AMD_Sync`。
2. 按一下 **VS Code**。
3. AMD Sync 會在 Ryzen AI Halo 上建立 `Documents/AMD_Sync/Project_1`,並在本機開啟 VS Code,並透過隧道連接到該資料夾。

現在您正在編輯位於 Ryzen AI Halo 上的檔案,並使用您本機的 VS Code 設定。建立 `helloworld.py`,加入 `print("hello world")`,開啟整合式終端機(`` Ctrl + ` ``),並執行它:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

狀態列顯示 **SSH: Linux** — 證明您的程式碼是在 Ryzen AI Halo 上執行,而非在您的筆記型電腦上。
### 試用終端機

點擊「終端機」即可透過 SSH 連線至相同資料夾，無需離開鍵盤即可操作。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

在 Windows 上，預設終端機為「PowerShell」— 如果您偏好其他選項，可從設定選單切換為「Windows 命令提示字元」。在 Linux 上，AMD Sync 會使用您系統的預設終端機。

---

## 目錄的運作方式

「目錄」下拉選單是 AMD Sync 中最重要的單一控制項 — 它決定您啟動的每個工具會在 Ryzen AI Halo 上的哪個位置存放。

- **`~/Documents/AMD_Sync`（預設值）** — 從此處啟動 VS Code 或 JupyterLab 會自動建立一個全新的專案資料夾（VS Code 為 `Project_1`、`Project_2`……；JupyterLab 為 `Notebook_Project_1`、`Notebook_Project_2`……）。
- **現有的專案資料夾** — `AMD_Sync` 的任何直接子資料夾（包括您在 Ryzen AI Halo 上手動建立的資料夾）都會顯示在下拉選單中。下次啟動時，系統會將您上次使用的資料夾設為預設值。
- **自訂路徑** — 輸入任何絕對路徑，即可開啟 Ryzen AI Halo 上其他位置的資料夾。AMD Sync 僅會「開啟」該資料夾 — 不會在 `AMD_Sync` 之外建立資料夾，且自訂路徑不會在多次工作階段之間儲存。

如果自訂路徑無法運作，AMD Sync 會告知原因：語法無效、資料夾不存在，或該路徑指向的是檔案而非資料夾。

---

## 即時效能指標與 JupyterLab

- **即時效能指標** — 即時顯示 GPU、記憶體與 CPU 使用率的儀表板。這是確認遠端訓練工作是否確實運用硬體資源的最快方式。
- **JupyterLab** — 透過 SSH 連線至 Ryzen AI Halo 的完整筆記本專案，並內建整合式終端機，讓您無需離開使用介面即可混合使用筆記本儲存格與 shell 指令。

---

## 設定與多台裝置

「設定」選單包含三個分頁：

| 分頁 | 涵蓋內容 |
|-----|----------------|
| **裝置** | 列出您成功連線過的每一台 Ryzen AI Halo。可重新連線、編輯憑證，或新增裝置。 |
| **資訊** | 提供文件與論壇支援的連結。 |
| **自訂** | 重新調整應用程式在桌面上的位置、切換終端機類型（僅限 Windows），以及檢查 AMD Sync 更新。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **終端機類型（Windows）** — 可在「PowerShell」（預設）與「Windows 命令提示字元」之間選擇。
- **終端機類型（Linux）** — 僅提供系統預設終端機可供使用。
- **應用程式更新** — 此分頁是從使用介面內檢查並安裝新版 AMD Sync 的正確位置；無需另外使用更新工具。

> 裝置僅在成功完成首次連線後才會顯示於「裝置」分頁中，因此連線失敗的嘗試不會使清單變得雜亂。

---

## 疑難排解

- **連線立即失敗** — 請確認 Developer Center 中 Ryzen AI Halo 的「遠端」分頁已啟用 SSH 伺服器。
- **密碼錯誤訊息** — 請在 Ryzen AI Halo 上使用您的「作業系統登入密碼」，而非從 Developer Center 取得的密碼。
- **VS Code 按鈕沒有反應** — 請從 [code.visualstudio.com](https://code.visualstudio.com) 在您的用戶端電腦上安裝 VS Code。
- **AMD Sync 系統匣圖示消失（Linux/GNOME）** — 請安裝並啟用 AppIndicator 擴充功能。
- **從檔案管理員無法開啟 `.deb` 檔** — 請在終端機中使用 `sudo apt install ./AMDSyncInstaller.deb`。
- **每次啟動都重新出現設定畫面（Linux）**：請解鎖您的登入金鑰圈，或使用 `--password-store=gnome-libsecret` 啟動，然後重新完成一次設定。

---