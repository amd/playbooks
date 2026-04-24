<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. Download the Windows ComfyUI v0.10.0 installer from [download.comfy.org](https://download.comfy.org/windows/nsis/x64).
2. Choose your hardware setup: Select `AMD ROCm`.
3. Choose where to install ComfyUI: Use the default path or your preferred folder.
4. Desktop App Settings: We recommend unselecting "Automatic Updates" to ensure you are using the recommended version of this app.
5. Press "Next" to begin installation.

<!-- @os:end -->

<!-- @os:linux -->
#### Clone ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (Optional) Checkout a specific version
```bash
git checkout v0.19.2
```

#### Install ComfyUI requirements

With the Python virtual environment activated, run:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **Note**: See [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI) for more information.

<!-- @os:end -->
