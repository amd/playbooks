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

> **Tip**: Use `lemonade --help` to display help information.


#### Checking Lemonade Server Status

Open a terminal and run:
```bash
lemonade status
```

You should see the output showing that the server is running, typically on port `13305`. 

The default OpenAI-compatible API base URL is: `http://localhost:13305/api/v1`.


#### Loading and Chatting with a Model

To load a model and open the Lemonade web app in your browser to chat with the model:
```bash
lemonade run Gemma-3-4b-it-GGUF
```

> **Tip**: Use `lemonade list` to see available models, or `lemonade pull <MODEL_NAME>` to download new ones.


#### Loading a Model with a Specific Backend

To load a llama.cpp model with AMD ROCm™ software backend:
```bash
lemonade run <MODEL_NAME> --llamacpp rocm
```

To load a llama.cpp model with Vulkan:
```bash
lemonade run <MODEL_NAME> --llamacpp vulkan
```


#### Setting a Default llama.cpp Backend

If you want Lemonade to use a default backend (for example, ROCm) for llama.cpp models, run:
```bash
lemonade config set llamacpp.backend=rocm
```

You can inspect the current config anytime with:
```bash
lemonade config
```

For the latest Lemonade server options or troubleshooting, please refer to the [official Lemonade documentation](https://lemonade-server.ai/docs/lemonade-cli/).