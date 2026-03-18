### GAIA

GAIA is AMD's open-source framework for building AI agents that run locally on AMD hardware with Ryzen AI acceleration.

#### Installing GAIA

<!-- @os:windows -->

1. Open PowerShell
2. Create a virtual environment and install GAIA:
```cmd
uv venv .venv
.\.venv\Scripts\Activate.ps1
uv pip install amd-gaia
```

<!-- @os:end -->

<!-- @os:linux -->

1. Open a terminal
2. Create a virtual environment and install GAIA:
```bash
uv venv .venv
source .venv/bin/activate
uv pip install amd-gaia
```

<!-- @os:end -->

#### Initializing GAIA

After installation, run `gaia init` to set up Lemonade Server and download models:

```
gaia init
```

This installs Lemonade Server, downloads the default models, and verifies the setup.

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
