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

# 使用 RCCL 叢集化兩台 Ryzen™ AI Halo

## 總覽

您的 Ryzen™ AI Halo 已經能夠在本機執行大型語言模型。而叢集化則能更進一步，透過本地網路結合多台系統的 GPU 記憶體，讓您能夠使用具備更強推理能力、更佳程式碼生成能力，以及更深入多語言理解能力的更大型模型，而這一切完全在您自己的硬體上完成。

本教學將教您如何使用 RCCL（ROCm Communication Collectives Library）搭配 vLLM 來叢集化兩台 Ryzen AI Halo 系統，並透過 ROCm 加速在兩台機器上執行擁有 397B 參數的 Qwen3.5-397B 模型。

## 您將學到什麼

- 如何在 Ryzen AI Halo 系統上擴充 VRAM 配置
- 啟動具備 ROCm 支援的 vLLM
- 為橫跨兩台 Ryzen AI Halo 系統的多節點張量平行推理配置 RCCL
- 在兩台聯網的 Ryzen AI Halo 系統上執行擁有 397B 參數的模型

## 先決條件

### 硬體

本教學需要兩台 Ryzen AI Halo 主機以及一台乙太網路交換器，以星型拓撲連接，每台主機皆直接以線路連至交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於支援多節點 Ryzen AI Halo 通訊的中央交換器（至少需 2 個埠） |
| 乙太網路線 | 2 | 連接每台 Halo 主機至交換器（建議使用 Cat 7 或以上規格） |

> **注意**：連接兩台 Ryzen AI Halo 主機需要兩個乙太網路交換器埠。若您是從獨立的客戶端機器（而非其中一台 Halo 主機）存取模型，則需要第三個埠。

### 軟體
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 實體硬體設置

> **注意**：請在機器 1 與機器 2 上都完成此步驟。

使用 Cat 7（或以上）線材將每台 Ryzen AI Halo 主機連接至乙太網路交換器。這將建立節點間高速通訊所使用的 10Gbps 連線。

### 1. 確認網路介面

在每台機器上，找出其網路介面名稱並記下（在後續說明中將以 `IFNAME` 表示）。執行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這會直接印出介面名稱，例如：

```bash
enp191s0
```

### 2. 驗證網路連線速度

確認連線是否已啟用並以全速運作，方法是檢查您的介面速度：

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**：請將 `<IFNAME>` 替換為 [1. 確認網路介面](#1-determine-network-interfaces) 中輸出的介面名稱

您應該會看到速度為 `10000Mb/s`：

```bash
	Speed: 10000Mb/s
```

> **注意**：若速度低於 `10000Mb/s` 或連線未啟用，請檢查纜線連接，並確認交換器埠已設定為 10Gbps。部分交換器需要停用自動協商，並手動設定連線速度；請參閱您所使用交換器的說明文件。

## 擴充 VRAM 配置

> **注意**：請在機器 1 與機器 2 上都完成此步驟。

### 執行大型模型的記憶體配置

在 Linux 上，ROCm 會使用共享的系統記憶體池，此記憶體池預設會配置為系統記憶體的一半。

透過以下說明，可以藉由變更核心的 Translation Table Manager（TTM）分頁設定來增加此配額。AMD 建議在 BIOS 中設定最小專用 VRAM（0.5 GB）。

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

## vLLM 容器初始化

> **注意**：請在機器 1 與機器 2 上都完成此步驟。

您的 Ryzen AI Halo 隨附一個已封裝於預先建置好的容器映像中的 vLLM，您可使用 Podman（一款免費開源的容器工具）來執行它。

### 1. 建立模型下載目錄

當您在本教學中提供 Qwen3.5-397B 模型服務時，vLLM 會自動將模型權重下載至您的系統。為確保容器內部能夠存取這些權重，請先建立一個可供容器掛載的模型目錄：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 啟動 vLLM 容器

以下指令會啟動容器並將您帶入互動式 shell。它會掛載您剛剛建立的模型目錄，並將您的 `IFNAME` 傳遞給 `NCCL_SOCKET_IFNAME` 與 `GLOO_SOCKET_IFNAME`，藉此告知 RCCL（vLLM 用來協調跨叢集 GPU 的函式庫）應使用哪個介面。

以下列指令啟動容器：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**：請將 `<IFNAME>` 替換為 [1. 確認網路介面](#1-determine-network-interfaces) 中輸出的介面名稱

## 在叢集上執行模型

vLLM 使用 Ray 來協調叢集，並使用 RCCL 處理跨節點的 GPU 對 GPU 通訊。其中一台機器擔任**主節點**（機器 1），負責協調推理；另一台則以**工作節點**身分加入（機器 2），提供其 GPU 記憶體與運算資源。

> **注意**：Ray 是 vLLM 的選用相依套件，僅能在預先配置好的 Podman 容器內使用。

在啟動時，vLLM 會使用張量平行技術將模型分割至兩個節點上。模型載入完成後，推理過程就如同在單一加速器上執行一般。

#### 防止 Ray OOM 錯誤

預設情況下，Ray 會監控每個節點的主機記憶體，並在記憶體使用率超過 95% 時終止最大的行程。在您的 Ryzen™ AI Halo 上，GPU 與主機共用同一個記憶體池，因此載入模型可能會觸發 `ray.exceptions.OutOfMemoryError` 並終止工作行程。

為防止此情況發生，我們將在啟動並加入叢集之前，於每台機器上匯出 `RAY_memory_monitor_refresh_ms=0`。
### 步驟 1:啟動 Ray Head Node(機器 1)

在機器 1 上,啟動 Ray head node 以初始化叢集:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **尋找 `<MACHINE_1_IP>`**:在機器 1 上,執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 步驟 2:加入叢集(機器 2)

在機器 2 上,連線至 head node 以組成叢集:

```bash
export RAY_memory_monitor_refresh_ms=0
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **尋找 `<MACHINE_2_IP>`**:在機器 2 上,執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 步驟 3:提供模型服務(機器 1)

在機器 1 上,啟動 vLLM 伺服器。這會自動下載模型並開始在兩個節點上提供服務:

```bash
vllm serve Qwen/Qwen3.5-397B-A17B-GPTQ-Int4 \
  --port 7000 \
  --host 0.0.0.0 \
  --max-model-len 32768 \
  --gpu-memory-utilization 0.9 \
  --dtype float16 \
  --tensor-parallel-size 2 \
  --distributed-executor-backend ray \
  --enforce-eager \
  --language-model-only \
  --reasoning-parser qwen3
```

#### 參數參考

| 旗標 | 用途 |
|------|---------|
| `--port` | 提供 HTTP API 服務的連接埠 |
| `--host` | 綁定伺服器的 IP 位址(`0.0.0.0` 代表所有介面) |
| `--max-model-len` | 最大內容長度(以 token 為單位) |
| `--gpu-memory-utilization` | 要分配的 GPU 記憶體比例(0.0–1.0) |
| `--dtype` | 模型權重的資料類型 |
| `--tensor-parallel-size` | 用於分割模型的 GPU 數量(設定為叢集中的 GPU 總數) |
| `--distributed-executor-backend` | 多節點執行的後端(叢集部署使用 `ray`) |
| `--enforce-eager` | 停用 CUDA graph 編譯以確保相容性 |
| `--language-model-only` | 跳過載入輔助模型元件(例如視覺編碼器) |
| `--reasoning-parser` | 為模型啟用結構化推理輸出剖析 |

如需完整的參數用法,請參閱 [vLLM 文件](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 存取模型

vLLM 提供與 OpenAI 相容的 API,因此您可以將任何相容的用戶端或介面連接到您的叢集。其中一個熱門選項是 [Open WebUI](https://github.com/open-webui/open-webui),它提供以瀏覽器為基礎的聊天介面。

若要將 Open WebUI 連接到您的 vLLM 端點:

1. 開啟 **Settings** > **Admin Panel** > **Connections**
2. 點擊 **Manage OpenAI API Connections** 上的 **+**
3. 將 **Connection Type** 設為 **External**
4. 將 **URL** 設為 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **Auth** 底下,從下拉選單選擇 **None**
6. 將 **Model IDs** 保持空白,以自動探索端點中的所有模型

> **尋找 `<MACHINE_1_IP>`**:在機器 1 上,執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。如果是從機器 1 本身存取 Open WebUI,您可以使用 `http://localhost:7000/v1`。

![vLLM 端點的 Open WebUI 連線設定](assets/openwebui-connection.png)

連線後,從 Open WebUI 的模型下拉選單中選擇模型並開始聊天。此模型現在正在您的兩個 Ryzen AI Halo 節點上執行:

![在 Open WebUI 中與 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 後續步驟

- **探索其他模型**:在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上探索符合您叢集總 GPU 記憶體的新模型
- **擴展至四個節點**:新增兩個額外的 Ryzen AI Halo 系統作為額外的 Ray workers,以在更多 GPU 上分割模型。這需要一個至少有四個連接埠的乙太網路交換器,每個節點各一個。在每個額外的 worker 上依照 [步驟 2:加入叢集](#step-2-join-the-cluster-machine-2) 的說明操作,並相應增加 `--tensor-parallel-size`
- **嘗試其他平行處理策略**:vLLM 支援用於混合專家(mixture-of-experts)模型的[專家平行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/),以及用於提升輸出量的[資料平行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。嘗試使用 `--enable-expert-parallel` 和 `--data-parallel-size` 來找出最適合您工作負載的組態