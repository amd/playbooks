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

## 概述

您的 Ryzen™ AI Halo 已經能夠在本地執行大型語言模型。透過叢集化,您可以進一步將多個系統的 GPU 記憶體透過本地網路結合,讓您能夠存取更大型的模型,擁有更強的推理能力、更佳的程式碼生成能力,以及更深入的多語言理解能力,而這一切都完全在您自己的硬體上完成。

本攻略將教您如何使用 RCCL(ROCm Communication Collectives Library)搭配 vLLM 叢集化兩台 Ryzen AI Halo 系統,並在兩台機器上以 ROCm 加速執行 Qwen3.5-397B,這是一個 397B 參數的模型。

## 您將學到什麼

- 如何在 Ryzen AI Halo 系統上擴充 VRAM 配置
- 啟動具備 ROCm 支援的 vLLM
- 為跨兩台 Ryzen AI Halo 系統的多節點張量並行推理配置 RCCL
- 在兩台聯網的 Ryzen AI Halo 系統上執行 397B 參數模型

## 先決條件

### 硬體

本攻略需要兩台 Ryzen AI Halo 裝置和一台乙太網路交換器,以星狀拓撲連接,每台裝置直接連接到交換器。

| 元件 | 數量 | 說明 |
|-----------|----------|-------------|
| Ryzen AI Halo | 2 | 組成叢集的運算節點 |
| 10Gbps 乙太網路交換器 | 1 | 用於允許多節點 Ryzen AI Halo 通訊的中央交換器(至少 2 個埠) |
| 乙太網路線 | 2 | 連接每台 Halo 裝置到交換器(建議使用 Cat 7 或更高規格) |

> **注意**:連接兩台 Ryzen AI Halo 裝置需要兩個乙太網路交換器埠。如果您是從獨立的客戶端機器(而非其中一台 Halo 裝置)存取模型,則需要第三個埠。

### 軟體
<!-- @os:linux -->
```bash
sudo apt install curl
```
<!-- @os:end -->

## 實體硬體設定

> **注意**:請在機器 1 和機器 2 上完成此步驟。

使用 Cat 7(或更高規格)的網路線將每台 Ryzen AI Halo 裝置連接到乙太網路交換器。這將建立用於節點間高速通訊的 10Gbps 連線。

### 1. 判斷網路介面

在每台機器上,找出其網路介面的名稱並記下(在其餘說明中將稱為 `IFNAME`)。執行:

```bash
ip route get 1.1.1.1 | grep -oP 'dev \K\S+'
```

這會直接印出介面名稱,例如:

```bash
enp191s0
```

### 2. 驗證網路連線速度

透過檢查介面速度來確認連線是否啟用且以全速運作:

```bash
sudo ethtool <IFNAME> | grep Speed
```

> **注意**:將 `<IFNAME>` 替換為 [1. 判斷網路介面](#1-determine-network-interfaces) 中輸出的介面名稱

您應該會看到速度為 `10000Mb/s`:

```bash
	Speed: 10000Mb/s
```

> **注意**:如果速度低於 `10000Mb/s` 或連線未啟用,請檢查纜線連接,並確認交換器連接埠已設定為 10Gbps。有些交換器需要停用自動協商並手動設定連線速度;請參閱您的交換器說明文件。

## 擴充 VRAM 配置

> **注意**:請在機器 1 和機器 2 上完成此步驟。

### 執行大型模型的記憶體配置

在 Linux 上,ROCm 使用共享系統記憶體池,此記憶體池預設配置為系統記憶體的一半。

透過以下說明變更核心的轉譯表管理員(Translation Table Manager,TTM)頁面設定,可以增加此數量。AMD 建議在 BIOS 中設定最小專用 VRAM(0.5 GB)。

* 安裝 pipx 公用程式,並將 pipx 安裝的 wheel 路徑加入系統搜尋路徑。

  ```bash
  sudo apt install pipx
  pipx ensurepath
  ```

* 從 PyPI 安裝 amd-debug-tools wheel。
  ```bash
  pipx install amd-debug-tools
  ```

* 執行 amd-ttm 工具來查詢共享記憶體的目前設定。
  ```bash
  amd-ttm
  ```

* 將共享記憶體設定重新配置為 **120 GB**:
  ```bash
  amd-ttm --set 120
  ```

* 重新啟動系統以使變更生效。

## vLLM 容器初始化

> **注意**:請在機器 1 和機器 2 上完成此步驟。

您的 Ryzen AI Halo 隨附一個預先建置在容器映像中的 vLLM,您可以使用 Podman(一個免費開源的容器工具)來執行它。

### 1. 建立模型下載目錄

當您在本攻略中提供 Qwen3.5-397B 模型時,vLLM 會自動將模型權重下載到您的系統中。為確保這些權重能從容器內部存取,請先建立一個容器可以掛載的模型目錄:

```bash
mkdir -p ~/.local/share/vLLM/models
```

### 2. 啟動 vLLM 容器

以下指令會啟動容器並將您帶入互動式殼層。它會掛載您剛剛建立的模型目錄,並將您的 `IFNAME` 傳遞給 `NCCL_SOCKET_IFNAME` 和 `GLOO_SOCKET_IFNAME`,告訴 RCCL(vLLM 用於協調跨叢集 GPU 的函式庫)要使用哪個介面。

啟動容器:

```bash
sudo podman run -it --name vllm_cluster --replace --pull missing --network=host --device /dev/kfd --device /dev/dri -v ~/.local/share/vLLM/models:/opt/vLLM/models --env HF_HOME=/opt/vLLM/models --entrypoint="bin/bash" --shm-size=64g --pids-limit=-1 -e NCCL_SOCKET_IFNAME=<IFNAME> -e GLOO_SOCKET_IFNAME=<IFNAME> oci-registry.ryai.dev/ryai-vllm:latest
```

> **注意**:將 `<IFNAME>` 替換為 [1. 判斷網路介面](#1-determine-network-interfaces) 中輸出的介面名稱

## 在叢集上執行模型

vLLM 使用 Ray 來協調叢集,並使用 RCCL 處理跨節點的 GPU 對 GPU 通訊。一台機器作為**主節點**(機器 1),負責協調推理。另一台則作為**工作節點**加入(機器 2),貢獻其 GPU 記憶體與運算能力。

> **注意**:Ray 是 vLLM 的選用相依套件,僅能在預先配置的 Podman 容器內使用。

啟動時,vLLM 會使用張量並行技術將模型分片到兩個節點上。載入完成後,推理過程就如同在單一加速器上執行一樣。

### 步驟 1:啟動 Ray 主節點(機器 1)

在機器 1 上,啟動 Ray 主節點以初始化叢集:

```bash
ray start --head --port=6379 --node-ip-address=<MACHINE_1_IP> --num-gpus=1
```

> **尋找 `<MACHINE_1_IP>`**:在機器 1 上,執行 `hostname -I | awk '{print $1}'` 以找出其本地 IP 位址。
### 步驟 2：加入叢集（Machine 2）

在 Machine 2 上，連線至頭端節點（head node）以組成叢集：

```bash
ray start --address=<MACHINE_1_IP>:6379 --node-ip-address=<MACHINE_2_IP> --num-gpus=1
```

> **尋找 `<MACHINE_2_IP>`**：在 Machine 2 上，執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。

### 步驟 3：提供模型服務（Machine 1）

在 Machine 1 上，啟動 vLLM 伺服器。這會自動下載模型，並開始跨兩個節點提供服務：

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
|------|------|
| `--port` | 提供 HTTP API 服務的連接埠 |
| `--host` | 伺服器綁定的 IP 位址（`0.0.0.0` 代表所有介面） |
| `--max-model-len` | 最大上下文長度（以 token 計） |
| `--gpu-memory-utilization` | 分配的 GPU 記憶體比例（0.0–1.0） |
| `--dtype` | 模型權重的資料型別 |
| `--tensor-parallel-size` | 用於分割模型的 GPU 數量（設定為叢集中的 GPU 總數） |
| `--distributed-executor-backend` | 多節點執行的後端（叢集部署使用 `ray`） |
| `--enforce-eager` | 停用 CUDA graph 編譯以提高相容性 |
| `--language-model-only` | 略過載入輔助模型元件（例如視覺編碼器） |
| `--reasoning-parser` | 為模型啟用結構化推理輸出解析 |

如需完整的參數使用說明，請參閱 [vLLM 文件](https://docs.vllm.ai/en/latest/configuration/engine_args/)。

## 存取模型

vLLM 提供與 OpenAI 相容的 API，因此您可以將任何相容的用戶端或介面連接至您的叢集。其中一個熱門的選擇是 [Open WebUI](https://github.com/open-webui/open-webui)，它提供基於瀏覽器的聊天介面。

若要將 Open WebUI 連接至您的 vLLM 端點：

1. 開啟 **Settings** > **Admin Panel** > **Connections**
2. 點選 **Manage OpenAI API Connections** 上的 **+**
3. 將 **Connection Type** 設定為 **External**
4. 將 **URL** 設定為 `http://<MACHINE_1_IP>:7000/v1`
5. 在 **Auth** 下方，從下拉選單中選擇 **None**
6. 讓 **Model IDs** 保持空白，以自動探索端點中的所有模型

> **尋找 `<MACHINE_1_IP>`**：在 Machine 1 上，執行 `hostname -I | awk '{print $1}'` 以找出其本機 IP 位址。若是從 Machine 1 本身存取 Open WebUI，您可以使用 `http://localhost:7000/v1`。

![vLLM 端點的 Open WebUI 連線設定](assets/openwebui-connection.png)

連線後，從 Open WebUI 的模型下拉選單中選取模型，即可開始聊天。此模型現已跨您兩個 Ryzen AI Halo 節點運行：

![在 Open WebUI 中與 Qwen3.5-397B 聊天](assets/openwebui-chat.png)

## 後續步驟

- **探索其他模型**：在 [Hugging Face](https://huggingface.co/models?&sort=trending) 上尋找適合您叢集合併 GPU 記憶體容量的新模型
- **擴展至四個節點**：新增兩台額外的 Ryzen AI Halo 系統作為額外的 Ray 工作節點，以將模型分割至更多 GPU 上。這需要一台至少有四個連接埠的乙太網路交換器，每個節點使用一個連接埠。在每台額外的工作節點上依照 [步驟 2：加入叢集](#step-2-join-the-cluster-machine-2) 進行操作，並相應地提高 `--tensor-parallel-size`
- **嘗試其他平行處理策略**：vLLM 支援用於混合專家（mixture-of-experts）模型的 [專家平行處理（expert parallel）](https://docs.vllm.ai/en/latest/serving/expert_parallel_deployment/)，以及用於提升輸送量的 [資料平行處理（data parallel）](https://docs.vllm.ai/en/latest/serving/data_parallel_deployment/)。可嘗試使用 `--enable-expert-parallel` 與 `--data-parallel-size`，找出最適合您工作負載的設定