<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Instalação da toolchain Distrobox

O fluxo de trabalho em toolbox em contentor necessita de `podman`, `distrobox`, e `pipx`:

```bash
sudo apt install -y podman distrobox pipx
```

<!-- @os:linux -->
<!-- @test:id=distrobox-installed-linux timeout=60 hidden=True -->
```bash
export PATH="$HOME/.local/bin:$PATH"
podman --version
distrobox version 2>/dev/null || distrobox --version
pipx --version
```
<!-- @test:end -->
<!-- @os:end -->