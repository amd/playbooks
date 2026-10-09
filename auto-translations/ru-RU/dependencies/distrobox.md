<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Установка набора инструментов Distrobox

Для рабочего процесса с контейнеризированным toolbox требуются `podman`, `distrobox` и `pipx`:

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