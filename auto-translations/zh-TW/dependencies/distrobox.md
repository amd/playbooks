<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 安裝 Distrobox 工具鏈

容器化的工具箱工作流程需要 `podman`、`distrobox` 和 `pipx`：

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