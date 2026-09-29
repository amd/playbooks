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

# 使用 RPC 叢集化四台 Ryzen™ AI Halo

## 概觀

您的 Ryzen™ AI Halo 已經能夠在本機執行大型語言模型。叢集化技術能更進一步，透過區域網路結合多個系統的 GPU 記憶體，讓您能夠存取具有更強推理能力、更佳程式碼產生能力，以及更深層多語言理解能力的更大型模型，而這一切都完全在您自己的硬體上執行。

本手冊將教您如何使用 llama.cpp 的 RPC 引擎叢集化四台 Ryzen AI Halo 系統，並在所有四台機器上以 AMD ROCm™ 加速執行 Kimi K2.6（一個大型混合專家模型）。

## 您將學到什麼

- 如何擴展 Ryzen AI Halo 系統上的 VRAM 配置
- 安裝具備 ROCm 及 RPC 支援的 llama.cpp
- 設定 RPC 工作站並在四個節點上啟動分散式推論
- 在四台連網的 Ryzen AI Halo 系統上執行 1T 參數的模型

## 設定記憶體配置

> **注意**：請在所有四台機器（機器 1 至機器 4）上完成此步驟。

<!-- @os:windows -->
在 Windows 上，若要執行需要更高記憶體的較大型模型，我們需要使用 AMD 可變圖形記憶體（iGPU VRAM）配置。

您可以開啟 AMD Software: Adrenalin Edition 控制面板，並導覽至：`Performance > Tuning > AMD Variable Graphics Memory`。將數值設定為 **96 GB**。請重新啟動系統以套用變更。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，ROCm 使用共享系統記憶體池，此記憶體池預設會配置為系統記憶體的一半。

您可以透過以下指示變更核心的轉譯表管理員（Translation Table Manager，TTM）頁面設定，來增加此數量。AMD 建議在 BIOS 中設定最小專用 VRAM（0.5 GB）。

* 安裝 pipx 工具，並將 pipx 安裝的 wheel 路徑加入系統搜尋路徑。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 從 PyPI 安裝 amd-debug-tools wheel。
  ```bash
  pipx install amd-debug-tools
  ```

* 執行 amd-ttm 工具以查詢目前的共享記憶體設定。
  ```bash
  amd-ttm
  ```

* 將共享記憶體設定重新配置為 **120 GB**：
  ```bash
  amd-ttm --set 120
  ```

* 重新啟動系統以套用變更。


<!-- @os:end -->
<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->
## 先決條件

### 硬體

本手冊需要四台 Ryzen AI Halo 裝置及一台乙太網路交換器，並以星型拓撲連接，每台裝置皆直接以纜線連接至交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於允許多節點 Ryzen AI Halo 通訊的中央交換器（至少 4 個連接埠） |
| 乙太網路纜線 | 4 | 連接每台 Halo 裝置與交換器（建議使用 Cat 7 或更高規格） |

> **注意**：連接四台 Ryzen AI Halo 裝置需要四個乙太網路交換器連接埠。若您要從獨立的用戶端機器（而非其中一台 Halo 裝置）存取模型，則需要第五個連接埠。

### 軟體
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
請安裝：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)，並選取 **Desktop Development with C++** 工作負載
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 實體硬體設定

> **注意**：請在所有四台機器（機器 1 至機器 4）上完成此步驟。

使用 Cat 7（或更高規格）纜線，將每台 Ryzen AI Halo 裝置連接至乙太網路交換器。這會建立節點間高速通訊所使用的 10Gbps 連線。
<!-- @os:linux -->
### 1. 確定網路介面

在每台機器上，找出其網路介面的名稱並記下（下文將以 `IFNAME` 稱之）。執行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這會直接印出介面名稱，例如：

```bash
enp191s0
```

### 2. 驗證網路連線速度

透過檢查您介面的速度，確認連線已啟用且以全速運作：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：請將 `<IFNAME>` 替換為 [1. 確定網路介面](#1-determine-network-interfaces) 中輸出的介面名稱

您應該會看到速度為 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：若速度低於 `10000Mb/s` 或連線未啟用，請檢查纜線連接並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連線速度；請參閱您交換器的說明文件。

<!-- @os:end -->

<!-- @os:windows -->
### 驗證網路連線速度

在每台機器上，檢查您網路介面的連線速度：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的乙太網路介面應為 `Up`，並以 `10 Gbps` 運作：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：若速度低於 `10 Gbps` 或連線未啟用，請檢查纜線連接並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連線速度；請參閱您交換器的說明文件。

<!-- @os:end -->

## 安裝 llama.cpp

> **注意**：請在所有四台機器（機器 1 至機器 4）上完成此步驟。

提供兩種安裝選項：

- [選項 1：Lemonade SDK（建議）](#option-1-lemonade-sdk-recommended) - 預先建置的二進位檔，設定速度最快
- [選項 2：手動原始碼建置](#option-2-manual-source-build) - 從原始碼建置，完全掌控建置旗標

### 選項 1：Lemonade SDK（建議）

Lemonade SDK 提供具備 AMD ROCm 7 加速的 llama.cpp 每夜建置版本，目標為 gfx1151（Strix Halo / Ryzen AI Max+ 395）等 GPU 及其他近期的 Radeon 架構。

<!-- @os:windows -->
#### 步驟 1：下載預先建置的二進位檔

前往最新版本頁面,下載符合您平台與 GPU 目標的封存檔:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的檔案(其中 `xxxx` 為建置編號)。

#### 步驟 2:解壓縮二進位檔

解壓縮下載的封存檔:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

此目錄現在包含已啟用 ROCm 的 `llama-cli.exe`、`llama-server.exe` 與 `ggml-rpc-server.exe` 建置版本,已針對您的 Ryzen AI Halo 系統預先編譯完成。

#### 步驟 3:驗證 GPU 偵測

```bash
.\llama-cli.exe --list-devices
```

預期輸出:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### 步驟 1:下載預先建置的二進位檔

前往最新版本頁面,下載符合您平台與 GPU 目標的封存檔:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的檔案(其中 `xxxx` 為建置編號)。

#### 步驟 2:解壓縮並準備二進位檔

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目錄現在包含已啟用 ROCm 的 `llama-cli`、`llama-server` 與 `rpc-server` 建置版本,已針對您的 Ryzen AI Halo 系統預先編譯完成。

#### 步驟 3:驗證 GPU 偵測

```bash
./llama-cli --list-devices
```

預期輸出:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
在每個節點上準備好 llama.cpp 之後,請繼續進行[下載模型](#downloading-the-model)。

### 選項 2:手動原始碼建置

<!-- @os:windows -->
#### 步驟 1:建置 llama.cpp

開啟 **x64 Native Tools Command Prompt**(隨 Visual Studio Build Tools 安裝)並複製儲存庫:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

將 HIP 加入您的路徑,並以 ROCm 與 RPC 支援進行建置:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm/HIP 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用分散式推論的 RPC |
| `-DGPU_TARGETS=gfx1151` | 針對 Ryzen AI Halo GPU(Radeon 8060s) |
| `-G Ninja` | 使用 Ninja 建置系統 |

#### 步驟 2:驗證 GPU 偵測

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

預期輸出:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### 步驟 3:將 HIP 加入您的使用者路徑

上述建置步驟僅為目前工作階段設定了 `%HIP_PATH%\bin`。若要讓 HIP 函式庫在任何終端機中皆可使用(而不僅限於 x64 Native Tools Command Prompt),請將其永久加入您的使用者 `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每個節點上準備好 llama.cpp 之後,請繼續進行[下載模型](#downloading-the-model)。
<!-- @os:end -->

<!-- @os:linux -->
#### 步驟 1:建置 llama.cpp

複製儲存庫:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

以 ROCm 與 RPC 支援進行建置:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用分散式推論的 RPC |
| `-DAMDGPU_TARGETS="gfx1151"` | 針對 Ryzen AI Halo GPU(Radeon 8060s) |

如需更多建置選項,請參閱 [llama.cpp 建置文件](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)。

#### 步驟 2:驗證 GPU 偵測

```bash
cd rocm/bin
./llama-cli --list-devices
```

預期輸出:

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

在每個節點上準備好 llama.cpp 之後,請繼續進行[下載模型](#downloading-the-model)。
<!-- @os:end -->

## 下載模型

本操作手冊使用來自 [Unsloth](https://huggingface.co/unsloth/Kimi-K2.6-GGUF/tree/main/UD-Q2_K_XL) 的 `UD-Q2_K_XL` 量化版本的 [Kimi K2.6](https://huggingface.co/moonshotai/Kimi-K2.6)。此量化版本可容納於四個 Ryzen AI Halo 節點的合併 GPU 記憶體中。

使用 Hugging Face CLI 下載 GGUF 檔案:
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/Kimi-K2.6-GGUF --include "UD-Q2_K_XL/*" --local-dir Kimi-K2.6-GGUF
```
<!-- @os:end -->

> **注意**:模型下載必須在機器 1(控制器)上完成。RPC 工作節點(機器 2、3 和 4)不需要模型檔案的本機副本。

## 在叢集上啟動模型

llama.cpp RPC(遠端程序呼叫)引擎允許單一 llama.cpp 執行個體透過網路將模型層卸載至遠端工作節點。一台機器擔任**控制器**(機器 1),負責處理權杖化、排程與協調。其他三台機器各自執行一個輕量級的 **RPC 伺服器**(機器 2、3 和 4),向控制器公開其 GPU 記憶體與運算能力。

在載入時,llama.cpp 會將模型分片至所有四個節點。載入完成後,推論作業的運行方式就如同在單一加速器上執行一般。RPC 會在幕後處理張量傳輸與同步作業。

### 步驟 1:啟動 RPC 伺服器(機器 2、3 和 4)

在機器 2、3 和 4 的每一台上,啟動 RPC 伺服器以向控制器公開其 GPU 資源:
<!-- @os:linux -->
```bash
./ggml-rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\ggml-rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| 旗標 | 用途 |
|------|---------|
| `-p` | 廣播 RPC 伺服器所使用的連接埠 |
| `-c` | 啟用大型張量的本機快取,避免在模型載入期間重複進行網路傳輸 |
| `--host` | 用於綁定 RPC 伺服器的 IP 位址(`0.0.0.0` 代表所有介面) |

如需更多選項,請參閱 [llama.cpp RPC 文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步驟 2:啟動模型(機器 1)

在機器 2、3 和 4 上執行 RPC 伺服器的情況下,使用 `llama-cli` 或 `llama-server` 從機器 1 啟動推論作業。
#### llama-cli

`llama-cli` 提供終端機介面，可直接與模型互動。它非常適合用於基準測試、除錯及低階實驗。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **尋找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在 Machine 2、3、4 上分別執行 `hostname -I | awk '{print $1}'`，即可查得其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：請在 Terminal（Powershell）中執行此命令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **尋找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在 Machine 2、3、4 上，於 Terminal（Powershell）中分別執行 `ipconfig | findstr /C:"IPv4"`，即可查得其本機 IP 位址。

<!-- @os:end -->

啟動後，`llama-cli` 會顯示模型載入進度，並進入互動式提示畫面，讓您可以直接與模型對話：

![llama-cli 在四個節點上執行 Kimi K2.6](assets/llama-cli-example.png)

#### llama-server

`llama-server` 透過持續運作的伺服器程序公開相同的推論引擎，並整合了網頁使用者介面以及與 OpenAI 相容的 HTTP API。對於長時間運行的部署、多使用者存取，以及與外部工具整合而言，這是較適合的介面。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/Kimi-K2.6-GGUF/UD-Q2_K_XL/Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  -b 4096 \
  -ub 4096 \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **尋找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在 Machine 2、3、4 上分別執行 `hostname -I | awk '{print $1}'`，即可查得其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：請在 Terminal（Powershell）中執行此命令。

```powershell
.\llama-server.exe `
  -m C:\path\to\Kimi-K2.6-GGUF\UD-Q2_K_XL\Kimi-K2.6-UD-Q2_K_XL-00001-of-00008.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  -b 4096 `
  -ub 4096 `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053
```

> **尋找 `<RPC_WORKER_2_IP>`、`<RPC_WORKER_3_IP>`、`<RPC_WORKER_4_IP>`**：在 Machine 2、3、4 上，於 Terminal（Powershell）中分別執行 `ipconfig | findstr /C:"IPv4"`，即可查得其本機 IP 位址。
<!-- @os:end -->

啟動後，在瀏覽器中開啟 `http://<HOST_IP>:8081`，即可存取內建的網頁使用者介面。此介面提供以瀏覽器為基礎的聊天介面，方便與模型互動：

![llama-server 網頁使用者介面在四個節點上執行 Kimi K2.6](assets/llama-server-example.png)

<!-- @os:linux -->
> **尋找 `<HOST_IP>`**：在 Machine 1 上執行 `hostname -I | awk '{print $1}'`，即可查得其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **尋找 `<HOST_IP>`**：在 Machine 1 上，於 Terminal（Powershell）中執行 `ipconfig | findstr /C:"IPv4"`，即可查得其本機 IP 位址。
<!-- @os:end -->

#### 參數參考

| 旗標 | 用途 |
|------|---------|
| `-m` | GGUF 模型檔案的路徑（請使用第一個分片，`00001-of-00008`） |
| `-c` | 內容脈絡大小（以 token 為單位）。數值越大，占用的記憶體越多 |
| `-fa on` | 啟用 rocWMMA Flash Attention，以提升在 AMD GPU 上的效能 |
| `-ngl 999` | 將所有模型層卸載至 GPU |
| `-lm none` | 將模型載入模式設為 `none`，停用記憶體映射，藉此在模型大小超過系統 RAM 但仍可容納於 VRAM 時縮短載入時間 |
| `-b` | 邏輯批次大小（以 token 為單位）。設為 4096 可在各節點間取得輸出量與記憶體使用量的平衡 |
| `-ub` | 用於提示詞處理的實體（微）批次大小。與 `-b` 相符可避免不必要的分塊額外負擔 |
| `--host` | 用於綁定 `llama-server` 的 IP（僅適用於 `llama-server`） |
| `--port` | 用於提供 HTTP API 服務的連接埠（僅適用於 `llama-server`） |
| `--rpc` | 以逗號分隔的 RPC 工作端點清單（`IP:port`） |

如需完整的參數使用說明，請參閱 [llama-cli 文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)與 [llama-server 文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 後續步驟

- **連接第三方應用程式**：`llama-server` 公開了與 OpenAI 相容的 API。將任何與 OpenAI 相容的應用程式（例如 Open WebUI）指向 `http://<HOST_IP>:8081`，並使用任意占位用的 API 金鑰（例如 `none`），即可連接至您的叢集
- **探索其他模型**：瀏覽 [Hugging Face](https://huggingface.co/models?search=gguf) 上的量化 GGUF 模型，找出符合您叢集整體 GPU 記憶體容量的模型
- **擴充至四個節點以上**：新增更多 Ryzen AI Halo 系統作為額外的 RPC 工作節點，即可使用超過 1 兆參數規模的模型。將額外的端點以逗號分隔清單傳遞給 `--rpc`（例如 `--rpc <RPC_WORKER_2_IP>:50053,<RPC_WORKER_3_IP>:50053,<RPC_WORKER_4_IP>:50053,<RPC_WORKER_5_IP>:50053`）