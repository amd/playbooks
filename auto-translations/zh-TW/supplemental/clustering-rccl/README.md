<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# 使用 RCCL 叢集化兩台 Ryzen™ AI Halo

## 概覽

您的 Ryzen™ AI Halo 已具備在本機執行大型語言模型的能力。叢集化更進一步，透過區域網路結合多台系統的 GPU 記憶體，讓您能夠存取更大型的模型，獲得更強的推理能力、更佳的程式碼生成效果，以及更深入的多語言理解，且完全在您自己的硬體上運行。

本 playbook 將教您如何使用 RCCL（ROCm Communication Collectives Library）搭配 vLLM 叢集化兩台 Ryzen AI Halo 系統，並透過 ROCm 加速在兩台機器上執行 Qwen3.5-397B（一個擁有 3970 億參數的模型）。

## 您將學到的內容

- 如何擴展 Ryzen AI Halo 系統的 VRAM 配置
- 以 ROCm 支援啟動 vLLM
- 為兩台 Ryzen AI Halo 系統之間的多節點張量並行推理配置 RCCL
- 在兩台聯網的 Ryzen AI Halo 系統上執行 3970 億參數模型

## 先決條件

### 硬體

本 playbook 需要兩台 Ryzen AI Halo 裝置及一台乙太網路交換器，以星狀拓撲連接，每台裝置直接以有線方式連接至交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於實現多節點 Ryzen AI Halo 通訊的中央交換器（至少需 2 個連接埠） |
| 乙太網路線 | 2 | 將每台 Halo 裝置連接至交換器（建議使用 Cat 7 或更高規格） |

> **注意**：連接兩台 Ryzen AI Halo 裝置需要兩個乙太網路交換器連接埠。若您從獨立的用戶端機器（而非其中一台 Halo 裝置）存取模型，則需要第三個連接埠。

### 軟體
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 實體硬體設定

> **注意**：請在機器 1 和機器 2 上分別完成此步驟。

使用 Cat 7（或更高規格）網路線將每台 Ryzen AI Halo 裝置連接至乙太網路交換器。這將建立用於節點間高速通訊的 10Gbps 連結。

### 1. 確認網路介面

在每台機器上，找出其網路介面名稱並記錄下來（在後續說明中將以 `IFNAME` 表示）。執行：

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這將直接輸出介面名稱，例如：

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

## 擴展 VRAM 配置

> **注意**：請在機器 1 和機器 2 上分別完成此步驟。

### 執行大型模型的記憶體配置

在 Linux 上，ROCm 使用共享系統記憶體池，此記憶體池預設配置為系統記憶體的一半。

可透過變更核心的 Translation Table Manager（TTM）頁面設定來增加此容量，請依照以下說明操作。AMD 建議在 BIOS 中設定最小專用 VRAM（0.5 GB）。

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

## vLLM 容器初始化

> **注意**：請在機器 1 和機器 2 上分別完成此步驟。

您的 Ryzen AI Halo 隨附預先建置的容器映像，其中已封裝 vLLM，您可使用 Podman（一款免費開源的容器工具）來執行它。

### 1. 建立模型下載目錄

當您在本 playbook 中提供 Qwen3.5-397B 模型服務時，vLLM 將自動將模型權重下載至您的系統。為確保這些權重可從容器內部存取，請先建立一個容器可掛載的 models 目錄：

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 啟動 vLLM 容器

以下指令將啟動容器並進入互動式 shell。它會掛載您剛建立的 models 目錄，並將您的 `IFNAME` 傳遞給 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`，告知 RCCL（vLLM 用於協調叢集中 GPU 的程式庫）要使用哪個介面。

使用以下指令啟動容器：

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**：請將 `<IFNAME>` 替換為[1. 確認網路介面](#1-determine-network-interfaces)中輸出的介面名稱

## 在叢集上執行模型

vLLM 使用 Ray 來協調叢集，並使用 RCCL 處理節點間的 GPU 對 GPU 通訊。其中一台機器作為**頭節點**（機器 1），負責協調推理；另一台作為**工作節點**（機器 2），貢獻其 GPU 記憶體和運算能力。

> **注意**：Ray 是 vLLM 的選用相依套件，僅可在預先配置的 Podman 容器內使用。

啟動時，vLLM 使用張量並行將模型分片至兩個節點。載入完成後，推理過程如同在單一加速器上執行。

### 步驟 1：啟動 Ray 頭節點（機器 1）

在機器 1 上，啟動 Ray 頭節點以初始化叢集：

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **尋找 `<MACHINE_1_IP>`**：在機器 1 上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 步驟 2：加入叢集（機器 2）

在機器 2 上，連接至頭節點以組成叢集：

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **尋找 `<MACHINE_2_IP>`**：在機器 2 上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 步驟 3：提供模型服務（機器 1）

在機器 1 上，啟動 vLLM 伺服器。這將自動下載模型並開始在兩個節點上提供服務：

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

#### 參數說明

| 旗標 | 用途 |
|------|---------|
| `--port` | 提供 HTTP API 服務的連接埠 |
| `--host` | 伺服器綁定的 IP 位址（`0.0.0.0` 表示所有介面） |
| `--max-model-len` | 以 token 為單位的最大上下文長度 |
| `--gpu-memory-utilization` | 配置的 GPU 記憶體比例（0.0–1.0） |
| `--dtype` | 模型權重的資料類型 |
| `--tensor-parallel-size` | 模型分片所跨越的 GPU 數量（設定為叢集中的 GPU 總數） |
| `--distributed-executor-backend` | 多節點執行的後端（叢集部署使用 `ray`） |
| `--enforce-eager` | 停用 CUDA 圖形編譯以確保相容性 |
| `--language-model-only` | 跳過載入輔助模型元件（例如視覺編碼器） |
| `--reasoning-parser` | 為模型啟用結構化推理輸出解析 |

如需完整的參數使用說明，請參閱 [vLLM 說明文件](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 存取模型

vLLM 提供與 OpenAI 相容的 API，因此您可以將任何相容的用戶端或介面連接至您的叢集。[Open WebUI](https://github.com/open-webui/open-webui) 是一個常見的選擇，它提供以瀏覽器為基礎的聊天介面。

若要將 Open WebUI 連接至您的 vLLM 端點：

1. 開啟**設定** > **管理面板** > **連線**
2. 點擊**管理 OpenAI API 連線**上的 **+**
3. 將**連線類型**設定為**外部**
4. 將 **URL** 設定為 `http://<MACHINE_1_IP>:7000/v1`
5. 在**驗證**下，從下拉選單選擇**無**
6. 將**模型 ID** 留空，以自動探索端點中的所有模型

> **尋找 `<MACHINE_1_IP>`**：在機器 1 上執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。若從機器 1 本身存取 Open WebUI，可使用 `http://localhost:7000/v1`。

![Open WebUI 的 vLLM 端點連線設定](assets/openwebui-connection.png)

連線後，從 Open WebUI 的模型下拉選單中選擇模型並開始聊天。該模型現在正在您的兩台 Ryzen AI Halo 節點上運行：

![在 Open WebUI 中與 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 後續步驟

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上探索符合您叢集合併 GPU 記憶體容量的新模型
- **擴展至四個節點**：新增兩台 Ryzen AI Halo 系統作為額外的 Ray 工作節點，將模型分片至更多 GPU。這需要一台至少有四個連接埠的乙太網路交換器，每個節點各一個。在每台額外的工作節點上依照[步驟 2：加入叢集](#step-2-join-the-cluster-machine-2)操作，並相應增加 `--tensor-parallel-size`
- **嘗試其他並行策略**：vLLM 支援混合專家模型的[專家並行](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)以及提高吞吐量的[資料並行](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。嘗試使用 `--enable-expert-parallel` 和 `--data-parallel-size`，為您的工作負載找到最佳配置