<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### 安裝 Lemonade

<!-- @os:windows -->
從 [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) 下載最新安裝程式並執行 `.msi` 檔案。

安裝完成後：
- `lemonade` CLI 會自動加入您的系統 PATH
- Lemonade 伺服器預期會在背景自動執行

您也可以從命令列進行靜默安裝：
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

如需其他發行版或從原始碼安裝，請參閱[完整安裝選項](https://lemonade-server.ai/docs/guide/install/)。
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

若您看到版本號碼，表示 Lemonade 已正確安裝並準備就緒。

以下是常用的 Lemonade CLI 指令快速參考：

| 指令 | 功能說明 |
| --- | --- |
| `lemonade --help` | 顯示所有可用指令與旗標。 |
| `lemonade --version` | 印出已安裝的 Lemonade 版本。 |
| `lemonade status` | 確認 Lemonade 伺服器是否正在執行且可連線。預設的 OpenAI 相容 API 基礎 URL 為 `http://localhost:13305/api/v1`。 |
| `lemonade list` | 列出您的 Lemonade 設定中可用的模型。 |
| `lemonade pull <MODEL_NAME>` | 下載模型但不啟動。 |
| `lemonade run <MODEL_NAME>` | 若需要則先下載模型，然後啟動以進行推論/對話。 |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | 使用 ROCm 後端啟動 llama.cpp 模型。 |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | 使用 Vulkan 後端啟動 llama.cpp 模型。 |
| `lemonade config` | 顯示目前的 Lemonade 設定值。 |
| `lemonade config set llamacpp.backend=rocm` | 將預設的 llama.cpp 後端設定為 ROCm。 |

如需最新的 Lemonade 伺服器選項或疑難排解，請參閱[官方 Lemonade 文件](https://lemonade-server.ai/docs/lemonade-cli/)。