<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installing uv

[uv](https://docs.astral.sh/uv/) is a fast Python package/environment manager. It provides a managed Python interpreter and installs dependencies.

<!-- @os:linux -->
Install uv with the official script:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

`uv` installs into `~/.local/bin`; make sure that directory is on your `PATH`.

<!-- @test:id=uv-installed-linux timeout=120 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
uv --version
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:windows -->
Install uv with the official script:

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Open a new terminal so the updated `PATH` takes effect, or refresh it in the current session:

```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable('Path','User') + ';' + [System.Environment]::GetEnvironmentVariable('Path','Machine')
```

<!-- @test:id=uv-installed-windows timeout=120 hidden=True -->
```powershell
uv --version
```
<!-- @test:end -->
<!-- @os:end -->
