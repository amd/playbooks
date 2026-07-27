<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### 安裝 Lemonade

<!-- @os:windows -->
從 [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) 下載最新的安裝程式，並執行 `.msi` 檔案。

安裝完成後：
- `lemonade` CLI 會自動加入系統 PATH
- Lemonade 伺服器預期會在背景自動執行

您也可以透過命令列進行靜默安裝：
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu：**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux（AUR）：**
```bash
yay -S lemonade-server
```

若使用其他發行版，或想從原始碼安裝，請參閱[完整安裝選項](https://lemonade-server.ai/docs/guide/install/)。
<!-- @os:end -->


#### 驗證 Lemonade 安裝

開啟終端機並執行：
```bash
lemonade --version
```

您應該會看到類似以下的輸出：
```
lemonade version x.y.z
```

如果看到版本編號，代表 Lemonade 已正確安裝並可供使用。

以下提供常用的 Lemonade CLI 指令，供您快速參考：

| 指令 | 功能 |
| --- | --- |
| `lemonade --help` | 顯示所有可用的指令與旗標。 |
| `lemonade --version` | 印出已安裝的 Lemonade 版本。 |
| `lemonade status` | 確認 Lemonade 伺服器是否正在執行並可連線。預設的 OpenAI 相容 API 基底 URL 為 `http://localhost:13305/api/v1`。 |
| `lemonade list` | 列出您的 Lemonade 環境中可用的模型。 |
| `lemonade pull <MODEL_NAME>` | 下載模型但不啟動它。 |
| `lemonade run <MODEL_NAME>` | 視需要下載模型，然後啟動以進行推論／聊天。 |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | 以 ROCm 後端啟動 llama.cpp 模型。 |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | 以 Vulkan 後端啟動 llama.cpp 模型。 |
| `lemonade config` | 顯示目前的 Lemonade 設定值。 |
| `lemonade config set llamacpp.backend=rocm` | 將預設的 llama.cpp 後端設為 ROCm。 |

如需最新的 Lemonade 伺服器選項或疑難排解，請參閱[官方 Lemonade 文件](https://lemonade-server.ai/docs/lemonade-cli/)。