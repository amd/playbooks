<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 拉取 ds4 工具箱容器镜像

`ds4-cockpit` 会在容器工具箱中运行 ds4 推理引擎。在 **Interactive Toolboxes** 选项卡中，选择最新可用的工具箱（例如 `ds4-rocm-7.2.4`），然后点击 **Create/Update** 以拉取镜像。

若要直接拉取镜像，请改为执行以下操作：

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

该工具箱的版本会随时间变化，因此下面的检查匹配的是镜像系列，而不是固定的标签。

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->