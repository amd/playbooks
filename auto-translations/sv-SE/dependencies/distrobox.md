<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Installera verktygskedjan Distrobox

Det containeriserade arbetsflödet för verktygslådan kräver `podman`, `distrobox` och `pipx`:

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