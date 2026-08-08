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

# 使用 RPC 叢集化兩個 Ryzen™ AI Halo

## 概觀

您的 Ryzen™ AI Halo 已經能夠在本機執行大型語言模型。叢集化更進一步,將多個系統的 GPU 記憶體透過本機網路結合,讓您能夠存取更大型的模型,擁有更強的推理能力、更好的程式碼生成能力,以及更深入的多語言理解能力,而這一切都完全在您自己的硬體上進行。

本手冊將教您如何使用 llama.cpp 的 RPC 引擎叢集化兩個 Ryzen AI Halo 系統,並在兩台機器上以 AMD ROCm™ 加速執行 GLM 4.7(一個 358B 參數的模型)。

## 您將學到什麼

- 如何在 Ryzen AI Halo 系統上擴充 VRAM 配置
- 安裝具備 ROCm 和 RPC 支援的 llama.cpp
- 設定 RPC 工作節點並在兩個節點間啟動分散式推理
- 在兩個網路連接的 Ryzen AI Halo 系統上執行 358B 參數的模型

## 設定記憶體配置

> **注意**:請在機器 1 與機器 2 上完成此步驟。

<!-- @os:windows -->
在 Windows 上,若要執行需要更高記憶體的較大型模型,我們需要使用 AMD Variable Graphics Memory(iGPU VRAM)配置。

您可以透過開啟 AMD Software: Adrenalin Edition 控制面板,並前往:`Performance > Tuning > AMD Variable Graphics Memory` 來完成此操作。將數值設定為 **96 GB**。請重新啟動系統以使變更生效。

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @os:end -->

<!-- @os:linux -->
在 Linux 上,ROCm 使用共用系統記憶體池,而此記憶體池預設配置為系統記憶體的一半。

可透過以下指示變更核心的 Translation Table Manager(TTM)頁面設定來增加此數量。AMD 建議在 BIOS 中設定最小專用 VRAM(0.5 GB)。

* 安裝 pipx 工具,並將 pipx 安裝的 wheel 路徑加入系統搜尋路徑中。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 從 PyPI 安裝 amd-debug-tools wheel。
  ```bash
  pipx install amd-debug-tools
  ```

* 執行 amd-ttm 工具以查詢目前的共用記憶體設定。
  ```bash
  amd-ttm
  ```

* 將共用記憶體設定重新配置為 **120 GB**:
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

本手冊需要兩台 Ryzen AI Halo 設備和一台乙太網路交換器,以星形拓撲連接,每台設備直接連接到交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於允許多節點 Ryzen AI Halo 通訊的中央交換器(至少 2 個連接埠) |
| 乙太網路線 | 2 | 將每台 Halo 設備連接到交換器(建議使用 Cat 7 或更高等級) |

> **注意**:連接兩台 Ryzen AI Halo 設備需要兩個乙太網路交換器連接埠。如果您是從另一台獨立的客戶端機器存取模型,而非從其中一台 Halo 設備存取,則需要第三個連接埠。

### 軟體
<!-- @os:windows -->
<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
<!-- @require:driver -->
<!-- @device:end -->
請安裝:
- [Git](https://git-scm.com/downloads/win)
- [Python](https://www.python.org/downloads/)
- [Visual Studio Build Tools](https://aka.ms/vs/17/release/vs_community.exe),並搭配 **Desktop Development with C++** 工作負載
- [AMD HIP SDK](https://www.amd.com/en/developer/resources/rocm-hub/hip-sdk.html)
<!-- @os:end -->

<!-- @os:linux -->
```bash
sudo apt install git cmake python3 python3-pip
```
<!-- @os:end -->

## 實體硬體設置

> **注意**:請在機器 1 與機器 2 上完成此步驟。

使用 Cat 7(或更高等級)纜線將每台 Ryzen AI Halo 設備連接到乙太網路交換器。這會建立用於節點間高速通訊的 10Gbps 連結。
<!-- @os:linux -->
### 1. 確定網路介面

在每台機器上,找出其網路介面的名稱並記錄下來(下文將稱之為 `IFNAME`)。執行:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這會直接印出介面名稱,例如:

```bash
enp191s0
```

### 2. 驗證網路連結速度

透過檢查介面速度來確認連結已啟用且以全速運行:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**:將 `<IFNAME>` 替換為[1. 確定網路介面](#1-determine-network-interfaces)輸出的介面名稱

您應該會看到速度為 `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **注意**:如果速度低於 `10000Mb/s` 或連結未啟動,請檢查纜線連接,並確認交換器連接埠已設定為 10Gbps。有些交換器需要停用自動協商並手動設定連結速度;請參閱您交換器的說明文件。

<!-- @os:end -->

<!-- @os:windows -->
### 驗證網路連結速度

在每台機器上,檢查您網路介面的連結速度:

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
```

您的乙太網路介面應顯示為 `Up`,並以 `10 Gbps` 運行:

```powershell
Name      Status  LinkSpeed
----      ------  ---------
Ethernet  Up      10 Gbps
```

> **注意**:如果速度低於 `10 Gbps` 或連結未啟動,請檢查纜線連接,並確認交換器連接埠已設定為 10Gbps。有些交換器需要停用自動協商並手動設定連結速度;請參閱您交換器的說明文件。

<!-- @os:end -->

## 安裝 llama.cpp

> **注意**:請在機器 1 與機器 2 上完成此步驟。

提供兩種安裝選項:

- [選項 1:Lemonade SDK(建議)](#option-1-lemonade-sdk-recommended) - 預先建置的二進位檔,設定速度最快
- [選項 2:手動原始碼建置](#option-2-manual-source-build) - 從原始碼建置,完全掌控建置旗標

### 選項 1:Lemonade SDK(建議)

Lemonade SDK 提供具備 AMD ROCm 7 加速功能的 llama.cpp 每夜建置版本,目標為 gfx1151(Strix Halo / Ryzen AI Max+ 395)等 GPU 及其他近期的 Radeon 架構。

<!-- @os:windows -->
#### Step 1: 下載預先建置的二進位檔

前往最新的發行頁面,下載符合您平台與 GPU 目標的封存檔:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-windows-rocm-gfx1151-x64.zip` 的檔案(其中 `xxxx` 為建置編號)。

#### Step 2: 解壓縮二進位檔

解壓縮下載的封存檔:

```bash
llama-bxxxx-windows-rocm-gfx1151-x64.zip
```

此目錄現在包含已針對您的 Ryzen AI Halo 系統預先編譯、支援 ROCm 的 `llama-cli.exe`、`llama-server.exe` 與 `rpc-server.exe` 建置版本。

#### Step 3: 驗證 GPU 偵測

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
#### Step 1: 下載預先建置的二進位檔

前往最新的發行頁面,下載符合您平台與 GPU 目標的封存檔:

[https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/](https://github.com/lemonade-sdk/llamacpp-rocm/releases/latest/)

下載名為 `llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip` 的檔案(其中 `xxxx` 為建置編號)。

#### Step 2: 解壓縮並準備二進位檔

```bash
unzip llama-bxxxx-ubuntu-rocm-gfx1151-x64.zip
cd llama-bxxxx-ubuntu-rocm-gfx1151-x64
chmod +x llama-cli llama-server rpc-server
```

此目錄現在包含已針對您的 Ryzen AI Halo 系統預先編譯、支援 ROCm 的 `llama-cli`、`llama-server` 與 `rpc-server` 建置版本。

#### Step 3: 驗證 GPU 偵測

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
在每個節點上準備好 llama.cpp 後,請繼續前往[下載模型](#downloading-the-model)。

### 選項 2:手動原始碼建置

<!-- @os:windows -->
#### Step 1: 建置 llama.cpp

開啟 **x64 Native Tools Command Prompt**(隨 Visual Studio Build Tools 安裝),並複製儲存庫:

```cmd
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

將 HIP 加入您的路徑,並使用 ROCm 與 RPC 支援進行建置:

```cmd
set PATH=%HIP_PATH%\bin;%PATH%
cmake -S . -B rocm -G Ninja -DGGML_HIP=ON -DGGML_RPC=ON -DGPU_TARGETS=gfx1151 -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ -DCMAKE_BUILD_TYPE=Release
cmake --build rocm --config Release
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm/HIP 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用分散式推論用的 RPC |
| `-DGPU_TARGETS=gfx1151` | 以 Ryzen AI Halo GPU(Radeon 8060s)為目標 |
| `-G Ninja` | 使用 Ninja 建置系統 |

#### Step 2: 驗證 GPU 偵測

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

#### Step 3: 將 HIP 加入您的使用者路徑

上述建置步驟僅為目前工作階段設定了 `%HIP_PATH%\bin`。若要讓 HIP 函式庫在任何終端機中都可使用(而不只是 x64 Native Tools Command Prompt),請將其永久加入您的使用者 `PATH`:

```cmd
powershell -Command "[System.Environment]::SetEnvironmentVariable('Path', [System.Environment]::GetEnvironmentVariable('Path', 'User') + ';%HIP_PATH%\bin', 'User')"
```

在每個節點上準備好 llama.cpp 後,請繼續前往[下載模型](#downloading-the-model)。
<!-- @os:end -->

<!-- @os:linux -->
#### Step 1: 建置 llama.cpp

複製儲存庫:

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
```

使用 ROCm 與 RPC 支援進行建置:

```bash
cmake -B rocm -DGGML_HIP=ON -DGGML_RPC=ON -DGGML_HIP_ROCWMMA_FATTN=ON -DAMDGPU_TARGETS="gfx1151"
cmake --build rocm --config Release -j$(nproc)
```

| 建置旗標 | 用途 |
|-----------|---------|
| `-DGGML_HIP=ON` | 啟用 ROCm 軟體堆疊 |
| `-DGGML_RPC=ON` | 啟用分散式推論用的 RPC |
| `-DGGML_HIP_ROCWMMA_FATTN=ON` | 在 AMD GPU 上啟用 rocWMMA 以增強 Flash Attention |
| `-DAMDGPU_TARGETS="gfx1151"` | 以 Ryzen AI Halo GPU(Radeon 8060s)為目標 |

如需更多建置選項,請參閱 [llama.cpp 建置文件](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)。

#### Step 2: 驗證 GPU 偵測

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

在每個節點上準備好 llama.cpp 後,請繼續前往[下載模型](#downloading-the-model)。
<!-- @os:end -->

## 下載模型

此操作手冊使用 [GLM 4.7](https://huggingface.co/zai-org/GLM-4.7),這是一個 3580 億參數的模型,採用來自 [Unsloth](https://huggingface.co/unsloth/GLM-4.7-GGUF/tree/main/UD-Q4_K_XL) 的 `Q4_K_XL` 量化版本。在此量化等級下,模型需要約 205GB 的儲存空間,並可容納於兩個 Ryzen AI Halo 節點的合併 GPU 記憶體中。

使用 Hugging Face CLI 下載 GGUF 檔案:
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

> **注意**:模型下載必須在 Machine 1(控制器)上完成。RPC 工作節點不需要本機端的模型檔案副本。

## 在叢集上啟動模型

llama.cpp RPC(遠端程序呼叫)引擎允許單一 llama.cpp 執行個體透過網路將模型層卸載至遠端工作節點。一台機器擔任**控制器**(Machine 1),負責分詞、排程與協調。另一台機器則執行輕量級的 **RPC 伺服器**(Machine 2),將其 GPU 記憶體與運算能力提供給控制器使用。

在載入時,llama.cpp 會將模型分片至兩個節點。載入完成後,推論的進行方式就如同在單一加速器上執行一樣。RPC 會在背後處理張量傳輸與同步作業。

### Step 1: 啟動 RPC 伺服器(Machine 2)

在 Machine 2 上,啟動 RPC 伺服器以將其 GPU 資源提供給控制器:
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
| `-p` | 廣播 RPC 伺服器的連接埠 |
| `-c` | 啟用大型張量的本機快取,避免在模型載入期間重複進行網路傳輸 |
| `--host` | 用於繫結 RPC 伺服器的 IP 位址(`0.0.0.0` 代表所有介面) |

如需更多選項,請參閱 [llama.cpp RPC 文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/rpc/README.md)。

### Step 2: 啟動模型(Machine 1)

在 Machine 2 上執行 RPC 伺服器後,從 Machine 1 使用 `llama-cli` 或 `llama-server` 啟動推論。

#### llama-cli

`llama-cli` 提供以終端機為基礎的介面,可直接與模型互動。非常適合用於效能評測、偵錯與低階實驗。

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

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:請在終端機(Powershell)中執行此指令。

```powershell
.\llama-cli.exe `
  -m C:\path\to\GLM-4.7-GGUF\UD-Q4_K_XL\GLM-4.7-UD-Q4_K_XL-00001-of-00005.gguf `
  -c 32768 `
  -fa on `
  -ngl 999 `
  --no-mmap `
  --rpc <RPC_WORKER_IP>:50053
```

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上,於終端機(Powershell)中執行 `ipconfig | findstr /C:"IPv4"` 以找出其本機 IP 位址。

<!-- @os:end -->

執行後,`llama-cli` 會顯示模型載入進度,並進入互動式提示介面,您可以直接在其中與模型對話:

![llama-cli 在兩個節點上執行 GLM 4.7](assets/llama-cli-example.png)
#### llama-server

`llama-server` 透過一個持久化的伺服器程序,連同整合的網頁 UI 與相容 OpenAI 的 HTTP API,公開相同的推論引擎。對於長時間執行的部署、多使用者存取,以及與外部工具的整合來說,這是較為理想的介面。

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

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上,執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **注意**:請在終端機(Powershell)中執行此命令。

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

> **尋找 `<RPC_WORKER_IP>`**:在 Machine 2 上,於終端機(Powershell)中執行 `ipconfig | findstr /C:"IPv4"` 以找出其本機 IP 位址。
<!-- @os:end -->

啟動後,在瀏覽器中開啟 `http://<HOST_IP>:8081` 即可存取內建的網頁 UI。這提供了一個以瀏覽器為基礎的聊天介面,可用於與模型互動:

![llama-server 網頁 UI 於兩個節點上執行 GLM 4.7](assets/llama-server-example.png)

<!-- @os:linux -->
> **尋找 `<HOST_IP>`**:在 Machine 1 上,執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。
<!-- @os:end -->

<!-- @os:windows -->
> **尋找 `<HOST_IP>`**:在 Machine 1 上,於終端機(Powershell)中執行 `ipconfig | findstr /C:"IPv4"` 以找出其本機 IP 位址。
<!-- @os:end -->

#### 參數參考

| 旗標 | 用途 |
|------|---------|
| `-m` | GGUF 模型檔案的路徑(請使用第一個分片 `00001-of-00005`) |
| `-c` | 以 token 為單位的上下文大小。數值越大,使用的記憶體越多 |
| `-fa on` | 啟用 rocWMMA Flash Attention,以提升 AMD GPU 上的效能 |
| `-ngl 999` | 將所有模型層卸載至 GPU |
| `--no-mmap` | 停用記憶體對映,當模型大小超過系統 RAM 但仍能容納於 VRAM 中時,可縮短載入時間 |
| `--host` | 用於繫結 `llama-server` 的 IP(僅適用於 `llama-server`) |
| `--port` | 提供 HTTP API 服務的連接埠(僅適用於 `llama-server`) |
| `--rpc` | 以逗號分隔的 RPC 工作端點清單(`IP:port`) |

如需完整的參數使用說明,請參閱 [llama-cli 說明文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/main/README.md)與 [llama-server 說明文件](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)。

## 後續步驟

- **連接第三方應用程式**:`llama-server` 公開了相容 OpenAI 的 API。將任何相容 OpenAI 的應用程式(例如 Open WebUI)指向 `http://<HOST_IP>:8081`,並使用任意佔位 API 金鑰(例如 `none`),即可連接至您的叢集
- **探索其他模型**:在 [Hugging Face](https://huggingface.co/models?search=gguf) 上瀏覽量化的 GGUF,找出適合您叢集組合 GPU 記憶體容量的模型
- **擴充至四個節點**:新增兩台 Ryzen AI Halo 系統作為額外的 RPC 工作端,即可存取達一兆參數規模的模型。將額外的端點以逗號分隔的清單方式傳遞給 `--rpc`(例如 `--rpc <IP1>:50053,<IP2>:50053,<IP3>:50053`)