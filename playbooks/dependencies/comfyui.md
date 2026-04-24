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

#### Create a Virtual Environment
<!-- @device:halo_box -->
On Linux, open a terminal in the directory of your choice and run the following prompt to create a venv with ROCm+Pytorch already installed:

```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llm-env --system-site-packages
source llm-env/bin/activate
```
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt -->
On Linux, open a terminal in the directory of your choice and run the following prompt to create a venv:

```bash
sudo apt update
sudo apt install -y python3-venv
python3 -m venv llm-env
source llm-env/bin/activate
```
<!-- @device:end -->

#### Clone ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### Optionally checkout a specific version
```bash
git checkout v0.17.2
```

#### Install ComfyUI requirements

With the Python virtual environment activated, run:
```bash
pip install -r requirements.txt
```

> **Note**: See [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI) for more information.

<!-- @os:end -->
