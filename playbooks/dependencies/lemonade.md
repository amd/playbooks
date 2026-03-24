<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### Installing Lemonade

<!-- @os:windows -->
Download the latest installer from [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) and run the `.msi` file. The installer adds `lemonade-server` to your system PATH automatically.

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

```
lemonade-server --version
```

You should see output like:

```
lemonade-server x.y.z
```

If you see a version number, Lemonade is installed and ready to go.


#### Starting Lemonade

To start the server, open a terminal and run:
```bash
lemonade-server serve
```

The server starts on `http://localhost:8000` with an OpenAI-compatible API at `/api/v1`.

To run a specific model immediately, use the `run` command:

```bash
lemonade-server run Gemma-3-4b-it-GGUF
```

> **Tip**: Use `lemonade-server list` to see available models, or `lemonade-server pull <MODEL_NAME>` to download new ones.

To start Lemonade server with ROCm backend:

```bash
lemonade-server serve --llamacpp rocm
```

For the latest installation options or troubleshooting, please refer to the official Lemonade documentation.