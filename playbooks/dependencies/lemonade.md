<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installing Lemonade

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
**Ubuntu (snap):**
```bash
sudo snap install lemonade-server
**Ubuntu:**

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
