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

# 使用 RCCL 叢集四台 Ryzen™ AI Halo

## 概觀

您的 Ryzen™ AI Halo 已經能夠在本機執行大型語言模型。叢集化則更進一步，透過本機網路結合多台系統的 GPU 記憶體，讓您能存取更大型的模型，具備更強的推理能力、更佳的程式碼生成能力，以及更深層的多語言理解能力，而這一切完全在您自己的硬體上運行。

本手冊將教您如何使用 RCCL（ROCm Communication Collectives Library，ROCm 通訊集合函式庫）搭配 vLLM 叢集四台 Ryzen AI Halo 系統，並在所有四台機器上以 ROCm 加速執行 Qwen3.5-397B（一個擁有 397B 參數的模型）。

## 您將學到什麼

- 如何擴充 Ryzen AI Halo 系統上的 VRAM 配置
- 如何啟動具備 ROCm 支援的 vLLM
- 如何在四台 Ryzen AI Halo 系統之間設定 RCCL，以實現多節點張量平行推理
- 如何在四台網路連接的 Ryzen AI Halo 系統上執行一個 397B 參數的模型

## 先決條件

### 硬體

本手冊需要四台 Ryzen AI Halo 裝置與一台乙太網路交換器，以星型拓撲連接，每台裝置直接以線材連至交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 4 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 允許多節點 Ryzen AI Halo 通訊的中央交換器（至少需要 4 個連接埠） |
| 乙太網路線 | 4 | 將每台 Halo 裝置連接至交換器（建議使用 Cat 7 或以上規格） |

> **注意**：連接四台 Ryzen AI Halo 裝置需要四個乙太網路交換器連接埠。如果您是從獨立的用戶端機器（而非其中一台 Halo 裝置）存取模型，則需要第五個連接埠。

### 軟體
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 實體硬體設定

> **注意**：請在所有四台機器（機器 1 至機器 4）上完成此步驟。

使用 Cat 7（或以上規格）線材將每台 Ryzen AI Halo 裝置連接至乙太網路交換器。這會建立節點之間用於高速通訊的 10Gbps 連結。

### 1. 判斷網路介面

在每台機器上，找出其網路介面的名稱並記下（在後續說明中將以 `IFNAME` 稱之）。執行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這會直接印出介面名稱，例如：

```bash
enp191s0
```

### 2. 驗證網路連結速度

透過檢查您的介面速度，確認連結已啟用並以全速運作：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：請將 `<IFNAME>` 替換為[1. 判斷網路介面](#1-determine-network-interfaces)中輸出的介面名稱

您應該會看到速度為 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：如果速度低於 `10000Mb/s` 或連結未建立，請檢查線材連接，並確認交換器連接埠已設定為 10Gbps。部分交換器需要停用自動協商並手動設定連結速度，請參閱您的交換器文件。

## 擴充 VRAM 配置

> **注意**：請在所有四台機器（機器 1 至機器 4）上完成此步驟。

### 執行大型模型的記憶體設定

在 Linux 上，ROCm 使用共享系統記憶體池，此記憶體池預設設定為系統記憶體的一半。

此數量可透過變更核心的 Translation Table Manager（TTM）頁面設定來增加，詳見以下說明。AMD 建議在 BIOS 中設定最小專用 VRAM（0.5 GB）。

* 安裝 pipx 工具，並將 pipx 已安裝套件的路徑加入系統搜尋路徑。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 從 PyPI 安裝 amd-debug-tools 套件。
  ```bash
  pipx install amd-debug-tools
  ```

* 執行 amd-ttm 工具以查詢目前的共享記憶體設定。
  ```bash
  amd-ttm
  ```

* 將共享記憶體設定重新設定為 **120 GB**：
  ```bash
  amd-ttm --set 120
  ```

* 重新啟動系統以套用變更。

## vLLM 容器初始化

> **注意**：請在所有四台機器（機器 1 至機器 4）上完成此步驟。

您的 Ryzen AI Halo 隨附一個預先建置的容器映像，其中封裝了 vLLM，您可使用 Podman（一款免費的開放原始碼容器工具）來執行它。

### 1. 建立模型下載目錄

當您在本手冊中啟動 Qwen3.5-397B 模型服務時，vLLM 會自動將模型權重下載至您的系統。為確保這些權重可從容器內部存取，請先建立一個可供容器掛載的模型目錄：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 啟動 vLLM 容器

下方指令會啟動容器並讓您進入互動式 shell。它會掛載您剛才建立的模型目錄，並將您的 `IFNAME` 傳遞給 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`，告知 RCCL（vLLM 用來協調整個叢集 GPU 的函式庫）應使用哪個介面。

使用以下指令啟動容器：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**：請將 `<IFNAME>` 替換為[1. 判斷網路介面](#1-determine-network-interfaces)中輸出的介面名稱

## 在叢集上執行模型

vLLM 使用 Ray 來協調叢集，並使用 RCCL 處理跨節點的 GPU 對 GPU 通訊。其中一台機器作為主節點（機器 1），負責協調推理工作。其餘三台則作為工作節點加入（機器 2、3 與 4），貢獻其 GPU 記憶體與運算能力。

> **注意**：Ray 是 vLLM 的選用相依套件，僅能從預先設定的 Podman 容器內使用。

啟動時，vLLM 會使用張量平行技術將模型分割至所有四個節點上。載入完成後，推理過程就如同在單一加速器上執行一般。

#### 避免 Ray 發生 OOM 錯誤

預設情況下，Ray 會監控每個節點上的主機記憶體使用量，並在記憶體使用率超過 95% 時終止最大的處理程序。在您的 Ryzen™ AI Halo 上，GPU 與主機共用同一記憶體池，因此載入模型可能會觸發 `ray.exceptions.OutOfMemoryError` 並終止工作處理程序。

為避免此情況，我們將在每台機器開始並加入叢集之前，先匯出 `RAY_memory_monitor_refresh_ms=0`。
### 第 1 步：啟動 Ray 頭節點（機器 1）

在機器 1 上，啟動 Ray 頭節點以初始化叢集：

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **尋找 `<MACHINE_1_IP>`**：在機器 1 上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 第 2 步：加入叢集（機器 2、3 和 4）

在機器 2、3 和 4 的每一台上，連線至頭節點以組成叢集：

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_N_IP> --num-gpus=1
```

> **尋找 `<MACHINE_N_IP>`**：在每台工作機器上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 第 3 步：提供模型服務（機器 1）

在機器 1 上，啟動 vLLM 伺服器。此動作會自動下載模型，並開始在全部四個節點上提供服務：

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 131072 \
  --gpu-memory-utilization 0.8 \
  --dtype float16 \
  --tensor-parallel-size 4 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### 參數參考

| 旗標 | 用途 |
|------|---------|
| `--port` | 用來提供 HTTP API 的連接埠 |
| `--host` | 繫結伺服器的 IP 位址（`0.0.0.0` 代表所有介面） |
| `--max-model-len` | 以權杖計的最大內容長度 |
| `--gpu-memory-utilization` | 要分配的 GPU 記憶體比例（0.0–1.0） |
| `--dtype` | 模型權重的資料型別 |
| `--tensor-parallel-size` | 用來分片模型的 GPU 數量（設為叢集中的 GPU 總數） |
| `--distributed-executor-backend` | 多節點執行所使用的後端（叢集部署請用 `ray`） |
| `--enforce-eager` | 停用 CUDA 圖編譯以確保相容性 |
| `--language-model-only` | 跳過載入輔助模型元件（例如視覺編碼器） |
| `--reasoning-parser` | 為模型啟用結構化推理輸出剖析 |

如需完整的參數用法，請參閱 [vLLM 文件](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 存取模型

vLLM 提供與 OpenAI 相容的 API，因此您可以將任何相容的用戶端或介面連線至您的叢集。其中一個熱門選擇是 [Open WebUI](https://github.com/open-webui/open-webui)，它提供以瀏覽器為基礎的聊天介面。

若要將 Open WebUI 連線至您的 vLLM 端點：

1. 開啟 **Settings** > **Admin Panel** > **Connections**
2. 點按 **Manage OpenAI API Connections** 上的 **+**
3. 將 **Connection Type** 設為 **External**
4. 將 **URL** 設為 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **Auth** 下，從下拉選單中選取 **None**
6. 將 **Model IDs** 保留空白，以自動探索端點中的所有模型

> **尋找 `<MACHINE_1_IP>`**：在機器 1 上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。如果是從機器 1 本身存取 Open WebUI，您可以使用 `http://localhost:7000/v1`。

![用於 vLLM 端點的 Open WebUI 連線設定](assets/openwebui-connection.png)

連線完成後，從 Open WebUI 的模型下拉選單中選取模型並開始聊天。此模型現已在您全部四台 Ryzen AI Halo 節點上執行：

![在 Open WebUI 中與 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 後續步驟

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上探索符合您叢集總 GPU 記憶體容量的新模型
- **擴充至四個節點以上**：加入更多 Ryzen AI Halo 系統作為額外的 Ray 工作節點，以將模型分片至更多 GPU 上。針對每台額外的工作機器，依照 [第 2 步：加入叢集（機器 2、3 和 4）](#step-2-join-the-cluster-machines-2-3-and-4) 操作，並相應地增加 `--tensor-parallel-size`
- **嘗試其他平行化策略**：vLLM 支援用於混合專家模型的 [專家平行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)，以及用於提升吞吐量的 [資料平行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。可嘗試使用 `--enable-expert-parallel` 和 `--data-parallel-size`，以找出最適合您工作負載的設定