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

# 使用 RPC 叢集化兩台 Ryzen™ AI Halo

## 總覽

您的 Ryzen™ AI Halo 已經能夠在本機執行大型語言模型。而叢集化則更進一步，透過本地網路結合多個系統的 GPU 記憶體，讓您能存取更大型的模型，具備更強的推理能力、更佳的程式碼產生能力，以及更深入的多語言理解能力，而這一切完全在您自己的硬體上進行。

本操作手冊將教您如何使用 llama.cpp 的 RPC 引擎叢集化兩台 Ryzen AI Halo 系統，並在兩台機器上以 AMD ROCm™ 加速執行 GLM 4.7（一個 358B 參數的模型）。

## 您將學到什麼

- 如何擴充 Ryzen AI Halo 系統的 VRAM 配置
- 安裝支援 ROCm 與 RPC 的 llama.cpp
- 設定 RPC 工作節點並啟動跨兩個節點的分散式推理
- 在兩台透過網路連接的 Ryzen AI Halo 系統上執行一個 358B 參數的模型

## 設定記憶體配置

> **注意**：請在機器 1 與機器 2 上皆完成此步驟。

<!-- @device:halo_box -->
<!-- @os:windows -->
> **執行接近或超過 128 GB 的模型**：在執行 Windows 的 AMD Ryzen™ AI Max 400 Series（Gorgon Halo）系統上，接近或超過 128 GB 記憶體的模型需要額外設定才能正常執行而不發生錯誤。請在載入模型前，依照 [AMD Ryzen AI Max PRO 400 Series Windows OS Guidelines](https://docs.amd.com/v/u/en-US/73342_1.00_AMD_Ryzen_AI_Max_PRO_400_Series_Windows_OS_Guidelines) 進行設定。
<!-- @os:end -->
<!-- @device:end -->

<!-- @os:windows -->
在 Windows 上，若要執行需要更高記憶體的大型模型，我們需要使用 AMD Variable Graphics Memory（iGPU VRAM）配置。

您可以開啟 AMD Software: Adrenalin Edition 控制面板，並導覽至：`Performance > Tuning > AMD Variable Graphics Memory` 來完成此設定。將數值設為 **96 GB**。請重新啟動系統以套用變更。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上，ROCm 使用共用的系統記憶體池，此記憶體池預設配置為系統記憶體的一半。

您可以透過下列步驟變更核心的 Translation Table Manager（TTM）頁面設定，以增加此配置量。AMD 建議在 BIOS 中將最小專用 VRAM 設定為最小值（0.5 GB）。

* 安裝 pipx 工具，並將 pipx 安裝的套件路徑加入系統搜尋路徑。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 從 PyPI 安裝 amd-debug-tools 套件。
  ```bash
  pipx install amd-debug-tools
  ```

* 執行 amd-ttm 工具以查詢目前的共用記憶體設定。
  ```bash
  amd-ttm
  ```

* 將共用記憶體設定重新配置為 **120 GB**：
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

本操作手冊需要兩台 Ryzen AI Halo 裝置與一台乙太網路交換器，以星狀拓撲連接，每台裝置皆直接以纜線連接至交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於支援多節點 Ryzen AI Halo 通訊的中央交換器（至少 2 個連接埠） |
| 乙太網路線 | 2 | 連接每台 Halo 裝置與交換器（建議使用 Cat 7 以上規格） |

> **注意**：連接兩台 Ryzen AI Halo 裝置需要兩個乙太網路交換器連接埠。若您是從獨立的用戶端機器（而非其中一台 Halo 裝置）存取模型，則需要第三個連接埠。

### 軟體
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
請安裝：
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe)（並選擇 **Desktop Development with C++** 工作負載）
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 實體硬體設定

> **注意**：請在機器 1 與機器 2 上皆完成此步驟。

使用 Cat 7（或以上規格）纜線，將每台 Ryzen AI Halo 裝置連接至乙太網路交換器。這會建立節點之間用於高速通訊的 10Gbps 連結。
<!-- @os:linux -->
### 1. 判斷網路介面

在每台機器上，找出其網路介面名稱並記錄下來（下文將以 `IFNAME` 表示）。執行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這會直接印出介面名稱，例如：

```bash
enp191s0
```

### 2. 驗證網路連結速度

請透過檢查介面速度，確認連結已啟用並以最高速度運作：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：請將 `<IFNAME>` 替換為 [1. 判斷網路介面](#1-determine-network-interfaces) 中輸出的介面名稱

您應會看到速度為 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：若速度低於 `10000Mb/s` 或連結未啟用，請檢查纜線連接狀況，並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連結速度，請參閱您交換器的說明文件。

<!-- @os:end -->

<!-- @os:windows -->
### 驗證網路連結速度

在每台機器上，檢查您網路介面的連結速度：

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的乙太網路介面應為 `Up` 狀態，並以 `10 Gbps` 運作：

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**：若速度低於 `10 Gbps` 或連結未啟用，請檢查纜線連接狀況，並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連結速度，請參閱您交換器的說明文件。

<!-- @os:end -->

## 安裝 llama.cpp

> **注意**：請在機器 1 與機器 2 上皆完成此步驟。

目前提供兩種安裝選項：

- [選項 1：Lemonade SDK（建議）](#option-1-lemonade-sdk-recommended) - 預先建置好的二進位檔，設定速度最快
- [選項 2：手動原始碼建置](#option-2-manual-source-build) - 從原始碼建置，完全掌控建置旗標
### 選項 1：Lemonade SDK（建議）

Lemonade SDK 提供搭載 AMD ROCm 7 加速功能的 llama.cpp 每日建置版本，可針對 gfx1151（Strix Halo / Ryzen AI Max+ 395）及其他近期 Radeon 架構進行運算。

<!-- @os:windows -->
#### 步驟 1：下載預先建置的二進位檔

前往最新發行版本頁面，下載符合您平台與 GPU 目標的壓縮檔：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的檔案（其中 `xxxx` 為建置編號）。

#### 步驟 2：解壓縮二進位檔

解壓縮下載的壓縮檔：

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

此目錄現在包含已啟用 ROCm 的 `llama-cli.exe`、`llama-server.exe` 與 `rpc-server.exe` 建置版本，皆已針對您的 Ryzen AI Halo 系統預先編譯完成。

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

前往最新發行版本頁面，下載符合您平台與 GPU 目標的壓縮檔：

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的檔案（其中 `xxxx` 為建置編號）。

#### 步驟 2：解壓縮並準備二進位檔

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目錄現在包含已啟用 ROCm 的 `llama-cli`、`llama-server` 與 `rpc-server` 建置版本，皆已針對您的 Ryzen AI Halo 系統預先編譯完成。

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

開啟 **x64 Native Tools Command Prompt**（隨 Visual Studio Build Tools 一併安裝），並複製儲存庫：

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

將 HIP 加入您的路徑中，並以 ROCm 與 RPC 支援進行建置：

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm/HIP 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用 RPC 以進行分散式推論 |
| `-DGPU_TARGETS=gfx1151` | 以 Ryzen AI Halo GPU（Radeon 8060s）為目標 |
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

上述建置步驟僅在目前工作階段中設定了 `%HIP_PATH%\bin`。若要讓 HIP 程式庫在任何終端機中都可使用（不僅限於 x64 Native Tools Command Prompt），請將其永久加入您的使用者 `PATH`：

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

以 ROCm 與 RPC 支援進行建置：

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用 RPC 以進行分散式推論 |
| `-DAMDGPU_TARGETS="gfx1151"` | 以 Ryzen AI Halo GPU（Radeon 8060s）為目標 |

如需更多建置選項，請參閱 [llama.cpp 建置文件](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)。

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

此指南使用 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7)，這是一個 358B 參數模型，採用來自 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) 的 `Q4_K_XL` 量化版本。在此量化等級下，此模型約需 205GB 儲存空間，並可容納於兩個 Ryzen AI Halo 節點的合併 GPU 記憶體中。

請使用 Hugging Face CLI 下載 GGUF 檔案：
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

> **注意**：模型下載必須在機器 1（控制器）上完成。RPC 工作節點不需要本機複製模型檔案。

## 在叢集上啟動模型

llama.cpp RPC（遠端程序呼叫）引擎可讓單一 llama.cpp 執行個體透過網路將模型層卸載至遠端工作節點。其中一台機器作為**控制器**（機器 1），負責權杖化、排程與協調作業。另一台機器則執行輕量級的 **RPC 伺服器**（機器 2），將其 GPU 記憶體與運算能力提供給控制器使用。

在載入階段，llama.cpp 會將模型切分至兩個節點上。載入完成後，推論作業便會如同在單一加速器上運行一般繼續進行。RPC 會在幕後處理張量傳輸與同步作業。

### 步驟 1：啟動 RPC 伺服器（機器 2）

在機器 2 上，啟動 RPC 伺服器以將其 GPU 資源提供給控制器使用：
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
| `-c` | 啟用大型張量的本機快取，避免在模型載入期間重複進行網路傳輸 |
| `--host` | 繫結 RPC 伺服器的 IP 位址（`0.0.0.0` 代表所有介面） |

如需更多選項，請參閱 [llama.cpp RPC 文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### 步驟 2：啟動模型（機器 1）

在機器 2 上執行 RPC 伺服器的情況下，請使用 `llama-cli` 或 `llama-server` 從機器 1 啟動推論作業。
#### llama-cli

`llama-cli` 提供終端機介面,可直接與模型互動。非常適合用於效能評測、偵錯和底層實驗。

<!-- @os:linux -->
```bash
./llama-cli \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上執行 `hostname -I | awk '{print $1}'` 以尋找其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:請在終端機 (Powershell) 中執行此命令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上的終端機 (Powershell) 中執行 `ipconfig | findstr /C:"IPv4"` 以尋找其本機 IP 位址。

<!-- @os:end -->

啟動後,`llama-cli` 會顯示模型載入進度,並進入互動式提示介面,讓您可以直接與模型聊天:

![llama-cli running GLM 4.7 across two nodes](assets/llama-cli-example.png)

#### llama-server

`llama-server` 透過持續執行的伺服器程序,搭配整合式網頁 UI 和與 OpenAI 相容的 HTTP API,公開同一個推論引擎。這是用於較長時間執行的部署、多使用者存取以及與外部工具整合的首選介面。

<!-- @os:linux -->
```bash
./llama-server \
  -m /path/to/GLM-4.7-GGUF/UD-Q4_K_XL/GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf \
  -c 32768 \
  -fa on \
  -ngl 999 \
  -lm none \
  --host 0.0.0.0 \
  --port 8081 \
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上執行 `hostname -I | awk '{print $1}'` 以尋找其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:請在終端機 (Powershell) 中執行此命令。

```powershell
.\llama-server.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  -lm none `
  --host 0.0.0.0 `
  --port 8081 `
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上的終端機 (Powershell) 中執行 `ipconfig | findstr /C:"IPv4"` 以尋找其本機 IP 位址。
<!-- @os:end -->

啟動後,在瀏覽器中開啟 `http://<HOST_IP>:8081` 即可存取內建的網頁 UI。此介面提供以瀏覽器為基礎的聊天介面,讓您與模型互動:

![llama-server web UI running GLM 4.7 across two nodes](assets/llama-server-example.png)

<!-- @os:linux -->
> **尋找 `<HOST_IP>`**:在 Machine 1 上執行 `hostname -I | awk '{print $1}'` 以尋找其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **尋找 `<HOST_IP>`**:在 Machine 1 上的終端機 (Powershell) 中執行 `ipconfig | findstr /C:"IPv4"` 以尋找其本機 IP 位址。
<!-- @os:end -->

#### 參數參考

| 旗標 | 用途 |
|------|---------|
| `-m` | GGUF 模型檔案的路徑(使用第一個分片 `00001-of-00005`) |
| `-c` | 上下文大小(以 token 為單位)。數值越大,使用的記憶體越多 |
| `-fa on` | 啟用 rocWMMA Flash Attention,以提升 AMD GPU 上的效能 |
| `-ngl 999` | 將所有模型層卸載到 GPU |
| `-lm none` | 將模型載入模式設定為 `none`,停用記憶體對應,以在模型大小超過系統 RAM 但可容納於 VRAM 時縮短載入時間 |
| `--host` | 要將 `llama-server` 綁定到的 IP(僅適用於 `llama-server`) |
| `--port` | 用於提供 HTTP API 服務的連接埠(僅適用於 `llama-server`) |
| `--rpc` | 以逗號分隔的 RPC 工作節點端點清單(`IP:port`) |

如需完整的參數使用方式,請參閱 [llama-cli documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md) 和 [llama-server documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 後續步驟

- **連接第三方應用程式**:`llama-server` 公開了與 OpenAI 相容的 API。將任何與 OpenAI 相容的應用程式(例如 Open WebUI)指向 `http://<HOST_IP>:8081`,並使用任意佔位 API 金鑰(例如 `none`),即可連接到您的叢集
- **探索其他模型**:在 [Hugging Face](https://huggingface.co/models?search=gguf) 上瀏覽量化的 GGUF,找出符合您叢集總 GPU 記憶體容量的模型
- **擴充至四個節點**:新增兩台 Ryzen AI Halo 系統作為額外的 RPC 工作節點,即可存取達 1 兆參數規模的模型。將額外的端點以逗號分隔清單的形式傳遞給 `--rpc`(例如 `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)