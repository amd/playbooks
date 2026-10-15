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

## 概觀

**AMD Sync** 能將您的筆記型電腦變成 AMD Ryzen™ AI Halo 的遠端控制中心。免去手動設定 SSH、金鑰與 IDE 的麻煩——安裝 AMD Sync，即可一鍵存取遠端終端機、VS Code、JupyterLab，以及 Ryzen AI Halo 上即時的 GPU/CPU/記憶體儀表板。

您的本機環境維持不變；每個指令、每份筆記本，以及每個模型都會在 Ryzen AI Halo 上執行。

> **提示**：本頁面將包含 AMDSync 的任何新更新。

## 您將學到什麼

- 在 Ryzen AI Halo 上啟用 SSH，並從 AMD Sync 連線至它
- 一鍵針對 Ryzen AI Halo 啟動 VS Code、終端機、JupyterLab 與即時效能指標
- 使用 AMD Sync 的受管理專案資料夾整理遠端工作

---

## 核心概念

AMD Sync 有兩端：**用戶端**（您的筆記型電腦，執行 AMD Sync 應用程式）與**伺服器端**（Ryzen AI Halo，執行 SSH 伺服器，AMD Sync 會透過此伺服器建立通道）。您從 AMD Sync 啟動的所有項目——VS Code、終端機、筆記本——都會在本機開啟，但實際在 Ryzen AI Halo 上執行。

> **支援的用戶端：** Windows 11 與 Linux。不支援 macOS。

---

## 步驟 1 — 在 Ryzen AI Halo 上啟用 SSH


> **注意：** 在 Windows 上，Ryzen AI Halo 出廠時*預設關閉* SSH 伺服器。在 Linux 上，則*預設開啟* SSH 伺服器。

1. 在 Ryzen AI Halo 上，開啟 **AMD Ryzen™ AI Developer Center**。
2. 前往 **Remote** 分頁。
3. 開啟 **SSH Server** 切換開關。
4. 記下 **Server Information** 下方顯示的 **IP Address**、**Port** 與 **Username**——稍後您將把這些值貼到 AMD Sync 中。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **注意：** 這是適用於 Windows 的 AMD Developer Center。Linux 版本的使用者介面可能不同，但遠端功能相似。

> **提示：** AMD Sync 詢問的是該使用者的**作業系統登入密碼**，而非 Developer Center 中的密碼。

---

## 步驟 2 — 在您的用戶端安裝 AMD Sync

AMD Sync 可在 Windows 11 與 Linux 上執行。請下載適用於您作業系統的安裝程式，並依照下列步驟操作。安裝完成後，在 **Get Started** 畫面點選 **Accept & Install**——完成後 AMD Sync 會自動啟動。

### Windows

[下載 AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. 雙擊 `AMDSyncInstaller.exe`。
2. 點選 **Accept & Install**。

> 若 Windows 防火牆出現提示，請允許 AMD Sync 存取網路，以便透過 SSH 連線至 Ryzen AI Halo。

### Linux

點選連結以下載您偏好的格式：

| 格式 | 下載 | 安裝指令 |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **注意：** Ubuntu App Center 可能會將本機開啟的 `.deb` 標記為「*可能不安全*」。這是任何第三方本機安裝程式的標準警告。若雙擊 `.deb` 失敗，請改用上方的終端機指令。

---

## 步驟 3 — 連線至您的 Ryzen AI Halo

首次啟動時，AMD Sync 會顯示 **Add a Remote Device** 表單。請使用 Developer Center 的 **Remote** 分頁中的數值填寫此表單。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| 欄位 | 說明 |
|-------|-------|
| **Device Name**（選填） | 例如 `Ryzen AI Halo` 這樣的易記標籤。預設為 `Device 1`、`Device 2`… |
| **Hostname or IP** | 來自 Remote 分頁 |
| **SSH Port** | 來自 Remote 分頁（僅限數字） |
| **Username** | 您在 Ryzen AI Halo 上的作業系統帳戶名稱 |
| **Password** | 您的作業系統登入密碼——輸入時會以遮罩顯示 |

點選 **Add Device**。經過短暫的載入畫面後，您會看到「**Connection Successful**」，並進入主畫面，該畫面位於您的系統匣中。點選視窗外部即可將其關閉；AMD Sync 仍會持續執行，並可一鍵開啟。

> **若連線失敗，** AMD Sync 會返回表單，並保留您輸入的數值。常見原因包括：Ryzen AI Halo 上的 SSH 未啟用、密碼錯誤，或兩台裝置位於不同網路。

---

## 步驟 4 — 啟動您的第一個遠端工具

主畫面提供五個一鍵元件——無論用戶端與 Ryzen AI Halo 執行哪一種作業系統皆可使用。

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| 元件 | 功能 |
|-----------|--------------|
| **Directory** | 選擇 Ryzen AI Halo 上的資料夾，VS Code、終端機與 JupyterLab 將在此資料夾中開啟。預設為受管理的 `Documents/AMD_Sync` 工作區。 |
| **VS Code** | 在本機開啟 VS Code，並透過 SSH 通道連接至所選資料夾。 |
| **Terminal** | 在所選資料夾中，開啟一個透過 SSH 連線至 Ryzen AI Halo 的本機終端機。 |
| **JupyterLab** | 啟動一個透過 SSH 連線至 Ryzen AI Halo 的筆記本專案，範圍限定於所選資料夾。 |
| **Live Metrics** | 即時檢視 Ryzen AI Halo 上的 GPU、記憶體與 CPU 使用率。 |

### 試用 VS Code

首次啟動時，請試用 **VS Code**。

1. 保留 **Directory** 為預設的 `~/Documents/AMD_Sync`。
2. 點選 **VS Code**。
3. AMD Sync 會在 Ryzen AI Halo 上建立 `Documents/AMD_Sync/Project_1`，並在本機開啟 VS Code，透過通道連接至該資料夾。

現在您正在使用本機的 VS Code 環境，編輯位於 Ryzen AI Halo 上的檔案。建立 `helloworld.py`，加入 `print("hello world")`，開啟整合終端機（`` Ctrl + ` ``），並執行它：

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

狀態列會顯示 **SSH: Linux**——證明您的程式碼是在 Ryzen AI Halo 上執行，而非在您的筆記型電腦上。
### 試用終端機

點選 **Terminal（終端機）** 即可透過 SSH 連線到相同資料夾，無需離開鍵盤。

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

在 Windows 上，預設終端機為 **PowerShell** —— 如果您偏好其他方式，可從設定選單切換為 **Windows Command Prompt**。在 Linux 上，AMD Sync 會使用您系統的預設終端機。

---

## Directory（目錄）的運作方式

**Directory（目錄）** 下拉式選單是 AMD Sync 中最重要的控制項——它決定您啟動的每個工具會落在 Ryzen AI Halo 上的哪個位置。

- **`~/Documents/AMD_Sync`（預設）** —— 從此處啟動 VS Code 或 JupyterLab 會自動建立一個全新的專案資料夾（VS Code 為 `Project_1`、`Project_2` 等；JupyterLab 為 `Notebook_Project_1`、`Notebook_Project_2` 等）。
- **既有的專案資料夾** —— `AMD_Sync` 的任何直接子資料夾（包括您在 Ryzen AI Halo 上手動建立的資料夾）都會出現在下拉式選單中。您上次使用的資料夾會成為下次的預設值。
- **自訂路徑** —— 輸入任何絕對路徑即可開啟 Ryzen AI Halo 上其他位置的資料夾。AMD Sync 只會*開啟*該資料夾——它不會在 `AMD_Sync` 之外建立資料夾，且自訂路徑不會在工作階段之間保留。

如果自訂路徑無法運作，AMD Sync 會告知原因：語法無效、資料夾不存在，或該路徑指向的是檔案。

---

## Live Metrics（即時指標）與 JupyterLab

- **Live Metrics（即時指標）** —— GPU、記憶體與 CPU 使用率的即時儀表板。這是確認遠端訓練作業是否確實使用到硬體的最快方式。
- **JupyterLab** —— 透過 SSH 連線到 Ryzen AI Halo 的完整筆記本專案，並附有專屬的整合終端機，讓您在不離開介面的情況下混合使用筆記本儲存格與 shell 指令。

---

## Settings（設定）與多台裝置

**Settings（設定）** 選單有三個分頁：

| 分頁 | 內容說明 |
|-----|----------------|
| **Devices（裝置）** | 列出您成功連線過的每一台 Ryzen AI Halo。可重新連線、編輯憑證，或新增裝置。 |
| **Information（資訊）** | 提供文件與論壇支援的連結。 |
| **Customize（自訂）** | 重新調整應用程式在您桌面上的位置、切換終端機類型（僅限 Windows），以及檢查 AMD Sync 更新。 |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **終端機類型（Windows）** —— 可在 **PowerShell**（預設）與 **Windows Command Prompt** 之間選擇。
- **終端機類型（Linux）** —— 僅提供預設的系統終端機。
- **應用程式更新** —— 這個分頁是從介面內檢查並安裝新版 AMD Sync 的正確位置；不需要另外的更新程式。

> 只有在成功首次連線後，裝置才會出現在 **Devices（裝置）** 底下，因此失敗的嘗試不會使清單變得雜亂。

---

## 疑難排解

- **連線立即失敗** —— 請確認 Developer Center 中 Ryzen AI Halo 的 **Remote（遠端）** 分頁上已啟用 SSH 伺服器。
- **密碼錯誤訊息** —— 請使用 Ryzen AI Halo 上的**作業系統登入密碼**，而不是從 Developer Center 取得的密碼。
- **VS Code 按鈕沒有反應** —— 請從 [code.visualstudio.com](https://code.visualstudio.com) 在您的用戶端電腦上安裝 VS Code。
- **AMD Sync 系統匣圖示消失（Linux/GNOME）** —— 請安裝並啟用 AppIndicator 擴充功能。
- **`.deb` 檔無法從檔案管理員開啟** —— 請在終端機中使用 `sudo apt install ./AMDSyncInstaller.deb`。
- **每次啟動都重新出現設定畫面（Linux）**：請解鎖您的登入鑰匙圈，或使用 `--password-store=gnome-libsecret` 啟動，然後重新完成一次設定。

---