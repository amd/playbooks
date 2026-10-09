<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Εγκατάσταση της αλυσίδας εργαλείων Distrobox

Η ροή εργασίας του containerized toolbox χρειάζεται τα `podman`, `distrobox` και `pipx`:

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