<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 RPC 叢集兩台 Ryzen™ AI Halo

## 概覽

您的 Ryzen™ AI Halo 已具備在本地端執行大型語言模型的能力。叢集化更進一步，透過區域網路結合多台系統的 GPU 記憶體，讓您能夠存取更大型的模型，獲得更強的推理能力、更佳的程式碼生成效果，以及更深入的多語言理解，且完全在您自己的硬體上執行。

本 playbook 將教您如何使用 llama.cpp 的 RPC 引擎叢集兩台 Ryzen AI Halo 系統，並透過 AMD ROCm™ 加速在兩台機器上執行 GLM 4.7（一個擁有 3580 億參數的模型）。

## 您將學到的內容

- 如何擴展 Ryzen AI Halo 系統的 VRAM 配置
- 安裝支援 ROCm 和 RPC 的 llama.cpp
- 設定 RPC 工作節點並在兩個節點間啟動分散式推理
- 在兩台聯網的 Ryzen AI Halo 系統上執行 3580 億參數模型

## 設定記憶體配置

> **注意**：請在機器 1 和機器 2 上都完成此步驟。

<!-- @os:windows -->
在 Windows 上，若要執行需要較高記憶體的大型模型，我們需要使用 AMD Variable Graphics Memory（iGPU VRAM）配置。

您可以開啟 AMD Software: Adrenalin Edition 控制面板，並導覽至：`Performance > Tuning > AMD Variable Graphics Memory`。將數值設定為 **96 GB**。請重新啟動系統以使變更生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，ROCm 使用共享系統記憶體池，此記憶體池預設配置為系統記憶體的一半。

您可以依照以下說明，透過變更核心的 Translation Table Manager（TTM）頁面設定來增加此數量。AMD 建議在 BIOS 中設定最小專用 VRAM（0.5 GB）。

* 安裝 pipx 工具，並將 pipx 安裝的 wheel 路徑加入系統搜尋路徑。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 從 PyPI 安裝 amd-debug-tools wheel。
  ```bash
  pipx install amd-debug-tools
  ```

* 執行 amd-ttm 工具以查詢共享記憶體的目前設定。
  ```bash
  amd-ttm
  ```

* 將共享記憶體設定重新配置為 **120 GB**：
  ```bash
  amd-ttm --set 120
  ```

* 重新啟動系統以使變更生效。


<!-- @os:end -->
<!-- @device:halo_box -->
## 檢查軟體更新

<!-- @require:software-update -->
<!-- @device:end -->
## 先決條件

### 硬體

本 playbook 需要兩台 Ryzen AI Halo 裝置和一台乙太網路交換器，以星狀拓撲連接，每台裝置直接以有線方式連接至交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於允許多節點 Ryzen AI Halo 通訊的中央交換器（至少 2 個連接埠） |
| 乙太網路線 | 2 | 將每台 Halo 裝置連接至交換器（建議使用 Cat 7 或更高規格） |

> **注意**：連接兩台 Ryzen AI Halo 裝置需要兩個乙太網路交換器連接埠。若您從獨立的用戶端機器（而非其中一台 Halo 裝置）存取模型，則需要第三個連接埠。

### 軟體
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
請安裝：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)，並選擇 **Desktop Development with C++** 工作負載
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 實體硬體設定

> **注意**：請在機器 1 和機器 2 上都完成此步驟。

使用 Cat 7（或更高規格）網路線將每台 Ryzen AI Halo 裝置連接至乙太網路交換器。這將建立用於節點間高速通訊的 10Gbps 連結。
<!-- @os:linux -->
### 1. 確認網路介面

在每台機器上，找到其網路介面名稱並記錄下來（以下將以 `IFNAME` 表示）。執行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這將直接印出介面名稱，例如：

```bash
enp191s0
```

### 2. 驗證網路連結速度

透過檢查介面速度，確認連結已啟用且以全速運行：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：請將 `<IFNAME>` 替換為[1. 確認網路介面](#1-determine-network-interfaces)中輸出的介面名稱

您應該會看到速度為 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：若速度低於 `10000Mb/s` 或連結未建立，請檢查網路線連接，並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連結速度；請參閱您的交換器說明文件。

<!-- @os:end -->

<!-- @os:windows -->
### 驗證網路連結速度

在每台機器上，檢查網路介面的連結速度：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的乙太網路介面應為 `Up` 狀態且以 `10 Gbps` 運行：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：若速度低於 `10 Gbps` 或連結未建立，請檢查網路線連接，並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連結速度；請參閱您的交換器說明文件。

<!-- @os:end -->

## 安裝 llama.cpp

> **注意**：請在機器 1 和機器 2 上都完成此步驟。

提供兩種安裝選項：

- [選項 1：Lemonade SDK（建議）](#option-1-lemonade-sdk-recommended) - 預先建置的二進位檔，設定最快速
- [選項 2：手動原始碼建置](#option-2-manual-source-build) - 從原始碼建置，可完全控制建置旗標

### 選項 1：Lemonade SDK（建議）

Lemonade SDK 提供每日建置的 llama.cpp，支援 AMD ROCm 7 加速，目標 GPU 包括 gfx1151（Strix Halo / Ryzen AI Max+ 395）及其他近期 Radeon 架構。

<!-- @os:windows -->
#### 步驟 1：下載預先建置的二進位檔

前往最新發布頁面，下載符合您平台和 GPU 目標的壓縮檔：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的檔案（其中 `xxxx` 為建置編號）。

#### 步驟 2：解壓縮二進位檔

解壓縮下載的壓縮檔：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

此目錄現在包含 ROCm 啟用的 `llama-cli.exe`、`llama-server.exe` 和 `rpc-server.exe` 建置，已針對您的 Ryzen AI Halo 系統預先編譯。

#### 步驟 3：驗證 GPU 偵測

```bash
.\llama-cli.exe --list-devices
```

預期輸出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```
<!-- @os:end -->

<!-- @os:linux -->
#### 步驟 1：下載預先建置的二進位檔

前往最新發布頁面，下載符合您平台和 GPU 目標的壓縮檔：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的檔案（其中 `xxxx` 為建置編號）。

#### 步驟 2：解壓縮並準備二進位檔

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目錄現在包含 ROCm 啟用的 `llama-cli`、`llama-server` 和 `rpc-server` 建置，已針對您的 Ryzen AI Halo 系統預先編譯。

#### 步驟 3：驗證 GPU 偵測

```bash
./llama-cli --list-devices
```

預期輸出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```
<!-- @os:end -->
在每個節點上準備好 llama.cpp 後，請繼續進行[下載模型](#downloading-the-model)。

### 選項 2：手動原始碼建置

<!-- @os:windows -->
#### 步驟 1：建置 llama.cpp

開啟 **x64 Native Tools Command Prompt**（隨 Visual Studio Build Tools 安裝）並複製儲存庫：

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

將 HIP 加入您的路徑，並以 ROCm 和 RPC 支援進行建置：

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm/HIP 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用 RPC 以進行分散式推理 |
| `-DGPU_TARGETS=gfx1151` | 目標為 Ryzen AI Halo GPU（Radeon 8060s） |
| `-G Ninja` | 使用 Ninja 建置系統 |

#### 步驟 2：驗證 GPU 偵測

```cmd
cd rocm\bin
.\llama-cli.exe --list-devices
```

預期輸出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon(TM) Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
  ROCm0: AMD Radeon(TM) Graphics (110511 MiB, 110357 MiB free)
```

#### 步驟 3：將 HIP 加入您的使用者路徑

上述建置步驟僅為目前工作階段設定了 `%HIP_PATH%\bin`。若要在任何終端機（而非僅限 x64 Native Tools Command Prompt）中使 HIP 程式庫可用，請將其永久加入您的使用者 `PATH`：

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每個節點上準備好 llama.cpp 後，請繼續進行[下載模型](#downloading-the-model)。
<!-- @os:end -->

<!-- @os:linux -->
#### 步驟 1：建置 llama.cpp

複製儲存庫：

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

以 ROCm 和 RPC 支援進行建置：

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用 RPC 以進行分散式推理 |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | 啟用 rocWMMA 以增強 AMD GPU 上的 Flash Attention |
| `-DAMDGPU_TARGETS="gfx1151"` | 目標為 Ryzen AI Halo GPU（Radeon 8060s） |

如需更多建置選項，請參閱 [llama.cpp 建置說明文件](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)。

#### 步驟 2：驗證 GPU 偵測

```bash
cd rocm/bin
./llama-cli --list-devices
```

預期輸出：

```bash
ggml_cuda_init: found 1 ROCm devices:
  Device 0: AMD Radeon Graphics, gfx1151 (0x1151), VMM: no, Wave Size: 32
Available devices:
ggml_backend_cuda_get_available_uma_memory: final available_memory_kb: 127697544
  ROCm0: AMD Radeon Graphics (120000 MiB, 124704 MiB free)
```

在每個節點上準備好 llama.cpp 後，請繼續進行[下載模型](#downloading-the-model)。
<!-- @os:end -->

## 下載模型

本 playbook 使用 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)，這是一個擁有 3580 億參數的模型，採用來自 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) 的 `Q4_K_XL` 量化版本。在此量化設定下，模型需要約 205GB 的儲存空間，並可容納於兩台 Ryzen AI Halo 節點的合併 GPU 記憶體中。

使用 Hugging Face CLI 下載 GGUF 檔案：
<!-- @os:linux -->
```bash
pip install huggingface-hub
hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

<!-- @os:windows -->
```cmd
python -m pip install -U huggingface-hub

$hfScripts = python -c "import sysconfig; print(sysconfig.get_path('scripts'))"
$env:Path = "$hfScripts;$env:Path"

hf download unsloth/GLM-4.7-GGUF --include "UD-Q4_K_XL/*" --local-dir GLM-4.7-GGUF
```
<!-- @os:end -->

> **注意**：模型下載必須在機器 1（控制器）上完成。RPC 工作節點不需要模型檔案的本地副本。

## 在叢集上啟動模型

llama.cpp RPC（遠端程序呼叫）引擎允許單一 llama.cpp 實例透過網路將模型層卸載至遠端工作節點。一台機器作為**控制器**（機器 1），負責處理標記化、排程和協調。另一台機器執行輕量級的 **RPC 伺服器**（機器 2），將其 GPU 記憶體和運算能力提供給控制器使用。

在載入時，llama.cpp 將模型分片至兩個節點。載入完成後，推理過程如同在單一加速器上執行。RPC 在幕後處理張量傳輸和同步。

### 步驟 1：啟動 RPC 伺服器（機器 2）

在機器 2 上，啟動 RPC 伺服器以將其 GPU 資源提供給控制器：
<!-- @os:linux -->
```bash
./rpc-server -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

<!-- @os:windows -->
```powershell
.\rpc-server.exe -p 50053 -c --host 0.0.0.0
```
<!-- @os:end -->

| 旗標 | 用途 |
|------|---------|
| `-p` | 廣播 RPC 伺服器的連接埠 |
| `-c` | 為大型張量啟用本地快取，避免模型載入期間重複進行網路傳輸 |
| `--host` | 綁定 RPC 伺服器的 IP 位址（`0.0.0.0` 表示所有介面） |

如需更多選項，請參閱 [llama.cpp RPC 說明文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步驟 2：啟動模型（機器 1）

在機器 2 上的 RPC 伺服器運行後，從機器 1 使用 `llama-cli` 或 `llama-server` 啟動推理。

#### llama-cli

`llama-cli` 提供終端機介面，可直接與模型互動。非常適合用於基準測試、除錯和低階實驗。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**：在機器 2 上，執行 `hostname -I | awk '{print $1}'` 以找到其本地 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：請在終端機（Powershell）中執行此命令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**：在機器 2 上，於終端機（Powershell）中執行 `ipconfig | findstr /C:"IPv4"` 以找到其本地 IP 位址。

<!-- @os:end -->

執行後，`llama-cli` 會顯示模型載入進度，並進入互動式提示，讓您可以直接與模型對話：

![llama-cli 在兩個節點上執行 GLM 4.7](assets/llama-cli-example.png)

#### llama-server

`llama-server` 透過持久性伺服器程序公開相同的推理引擎，並提供整合式網頁 UI 和相容 OpenAI 的 HTTP API。這是長期運行部署、多使用者存取以及與外部工具整合的首選介面。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  --no-mmap \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**：在機器 2 上，執行 `hostname -I | awk '{print $1}'` 以找到其本地 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**：請在終端機（Powershell）中執行此命令。

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**：在機器 2 上，於終端機（Powershell）中執行 `ipconfig | findstr /C:"IPv4"` 以找到其本地 IP 位址。
<!-- @os:end -->

啟動後，在瀏覽器中開啟 `http://<HOST_IP>:8081` 以存取內建網頁 UI。這提供了一個基於瀏覽器的聊天介面，可與模型互動：

![llama-server 網頁 UI 在兩個節點上執行 GLM 4.7](assets/llama-server-example.png)

<!-- @os:linux -->
> **尋找 `<HOST_IP>`**：在機器 1 上，執行 `hostname -I | awk '{print $1}'` 以找到其本地 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **尋找 `<HOST_IP>`**：在機器 1 上，於終端機（Powershell）中執行 `ipconfig | findstr /C:"IPv4"` 以找到其本地 IP 位址。
<!-- @os:end -->

#### 參數參考

| 旗標 | 用途 |
|------|---------|
| `-m` | GGUF 模型檔案的路徑（使用第一個分片，`00001-of-00005`） |
| `-c` | 以標記為單位的上下文大小。數值越大使用的記憶體越多 |
| `-fa on` | 啟用 rocWMMA Flash Attention 以提升 AMD GPU 上的效能 |
| `-ngl 999` | 將所有模型層卸載至 GPU |
| `--no-mmap` | 停用記憶體映射，當模型大小超過系統 RAM 但可容納於 VRAM 時可縮短載入時間 |
| `--host` | 綁定 `llama-server` 的 IP（僅限 `llama-server`） |
| `--port` | 提供 HTTP API 的連接埠（僅限 `llama-server`） |
| `--rpc` | 以逗號分隔的 RPC 工作節點端點清單（`IP:port`） |

如需完整的參數使用說明，請參閱 [llama-cli 說明文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)和 [llama-server 說明文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 後續步驟

- **連接第三方應用程式**：`llama-server` 公開相容 OpenAI 的 API。將任何相容 OpenAI 的應用程式（例如 Open WebUI）指向 `http://<HOST_IP>:8081`，並使用任意佔位 API 金鑰（例如 `none`）即可連接至您的叢集
- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?search=gguf) 上瀏覽量化的 GGUF 模型，尋找適合您叢集合併 GPU 記憶體的模型
- **擴展至四個節點**：新增兩台 Ryzen AI Halo 系統作為額外的 RPC 工作節點，以存取兆參數規模的模型。以逗號分隔的清單形式將額外端點傳遞給 `--rpc`（例如 `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`）