<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

The GAIA playbook requires a Lemonade server to be installed and running locally at `:13305` port. The `LemonadeClient`, included in the GAIA package, utilizes this server to obtain AMD accelerated hardware system information and model catalog queries.

#### Installing Lemonade

<!-- @device:halo_box -->
<!-- @os:linux -->
For HaloBox systems, which are based on the Debian Unix Distribution, the installation of Lemonade should be performed via Snap. [Install Lemonade Desktop on Debian using the Snap Store | Snapcraft](https://snapcraft.io/install/lemonade-desktop/debian) Below are the steps to install the Lemonade server: 

**Debian**
```bash 
sudo apt update 
sudo apt install snapd 
sudo snap install lemonade-server 
# (Optional) Install Lemonade Desktop 
sudo snap install lemonade-desktop 
``` 
<!-- @device:end --> 
<!-- @os:end -->

<!-- @os:windows -->
Download the latest installer from [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) and run the `.msi` file. 

After installation:
- The `lemonade` CLI is added to your system PATH automatically
- Lemonade server is expected to run in the background automatically

You can also install silently from the command line:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

For other distributions or to install from source, see the [full installation options](https://lemonade-server.ai/install_options.html).
<!-- @os:end -->


#### Verifying Lemonade Installation

Open a terminal and run:
```bash
lemonade --version
```

You should see output like:
```
lemonade version x.y.z
```

If you see a version number, Lemonade is installed correctly and ready to go.

For quick reference, here are common Lemonade CLI commands:

| Command | What it does |
| --- | --- |
| `lemonade --help` | Shows all available commands and flags. |
| `lemonade --version` | Prints the installed Lemonade version. |
| `lemonade status` | Confirms whether the Lemonade server is running and reachable. The default OpenAI-compatible API base URL is `http://localhost:13305/api/v1`. |
| `lemonade list` | Lists models available to your Lemonade setup. |
| `lemonade pull <MODEL_NAME>` | Downloads a model without launching it. |
| `lemonade run <MODEL_NAME>` | Downloads the model if needed, then starts it for inference/chat. |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | Starts a llama.cpp model with the ROCm backend. |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | Starts a llama.cpp model with the Vulkan backend. |
| `lemonade config` | Displays the current Lemonade configuration values. |
| `lemonade config set llamacpp.backend=rocm` | Sets the default llama.cpp backend to ROCm. |

For the latest Lemonade server options or troubleshooting, please refer to the [official Lemonade documentation](https://lemonade-server.ai/docs/lemonade-cli/).
