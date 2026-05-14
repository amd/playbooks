<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### GAIA

GAIA is AMD's open-source framework for building AI agents that run locally on AMD hardware with Ryzen AI acceleration.

#### Installing GAIA

**Method 1: Installation with Pip (Recommended)**

For a simpler and more straightforward installation, use pip to install the AMD-GAIA SDK. This method is recommended for most users. Follow the instructions provided in the GitHub release page [Developer install (Python CLI)](https://github.com/amd/gaia/releases/tag/v0.17.6). Use the following command to install the SDK: 

1. Open PowerShell
2. Create a virtual environment and install GAIA:
```cmd
python3 -m venv gaia-env
.\gaia-env\Scripts\Activate.ps1
pip install amd-gaia
```

<!-- @os:end -->

<!-- @os:linux -->

1. Open a terminal
2. Create a virtual environment and install GAIA:
```bash
python3 -m venv gaia-env
source gaia-env/bin/activate
pip install amd-gaia
```
<!-- @os:end -->

**Method 2: Build from Source**

To build the AMD-GAIA SDK from source, follow the detailed instructions provided in the official [Install GAIA](https://amd-gaia.ai/docs/guides/install#download) documentation. This method involves downloading the source code from the GitHub Release page in `Assets` section and compiling it on your system.  

<!-- @os:linux --> 
```bash 
# Download the installer from GitHub Releases 
wget gaia-agent-ui-X.Y.Z-x64-setup.exe 

chmod +x gaia-agent-ui-X.Y.Z-x64-setup.exe 

# Run the installer 
sudo apt install ./gaia-agent-ui-X.Y.Z-amd64.deb 
``` 
<!-- @os:end --> 

<!-- @os:windows --> 
```powershell 
# Download the installer from GitHub Releases 
Invoke-WebRequest -Uri "https://github.com/your-repo/releases/download/vX.Y.Z/gaia-agent-ui-X.Y.Z-x64-setup.exe" -OutFile "gaia-agent-ui-X.Y.Z-x64-setup.exe" 

# Run the installer 
Start-Process -FilePath ".\gaia-agent-ui-X.Y.Z-x64-setup.exe" -Wait 
``` 
<!-- @os:end --> 
<!-- @os:windows -->


#### Initializing GAIA

After installation, run `gaia init` to set up Lemonade Server and download models:

```
gaia init
```

This installs Lemonade Server, downloads the default models, and verifies the setup.

<!-- @test:id=gaia-lemonade-version timeout=60 hidden=True -->
```bash
lemonade --version
```
<!-- @test:end --> 


#### Verifying Installation

Verify that GAIA v0.16.2 or later is installed:

```
gaia --version
```

Then run a quick test to confirm GAIA is working:

```
gaia chat
```

Type a message and press Enter. Type `quit` to exit.

> **Important**: Make sure Lemonade Server is running before using GAIA. GAIA requires Lemonade Server to be started manually.

For more information, see the [GAIA documentation](https://amd-gaia.ai).
