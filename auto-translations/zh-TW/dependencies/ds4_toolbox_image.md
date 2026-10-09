<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### 提取 ds4 toolbox 容器映像檔

`ds4-cockpit` 會在容器 toolbox 內執行 ds4 推論引擎。在 **Interactive Toolboxes** 分頁中，選擇最新可用的 toolbox（例如 `ds4-rocm-7.2.4`），然後點擊 **Create/Update** 以提取映像檔。

若要改為直接提取映像檔：

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

由於 toolbox 版本會隨時間變動，下方的檢查會比對映像檔系列，而非固定的標籤。

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->