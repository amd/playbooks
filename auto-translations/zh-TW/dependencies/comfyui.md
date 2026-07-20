<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. 從 [download.comfy.org](https://download.comfy.org/windows/nsis/x64) 下載最新的 Windows ComfyUI 安裝程式。
2. 選擇您的硬體設定：選取 `AMD ROCm`。
3. 選擇要安裝 ComfyUI 的位置：使用預設路徑或您偏好的資料夾。
4. 桌面應用程式設定：我們建議取消勾選「自動更新」，以確保您使用的是此應用程式的建議版本。
5. 按下「Next」開始安裝。

<!-- @os:end -->

<!-- @os:linux -->
#### 複製 ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### （選用）切換至特定版本
```bash
git checkout v0.19.2
```

#### 安裝 ComfyUI 相依套件

啟用 Python 虛擬環境後，執行：
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **注意**：如需更多資訊，請參閱 [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI)。

<!-- @os:end -->