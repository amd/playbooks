<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4 toolbox コンテナイメージのプル

`ds4-cockpit` はコンテナ toolbox 内で ds4 推論エンジンを実行します。**Interactive Toolboxes** タブで、利用可能な最新の toolbox（例: `ds4-rocm-7.2.4`）を選択し、**Create/Update** をクリックしてイメージをプルします。

代わりに直接イメージをプルするには:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

toolbox のバージョンは時間とともに変化するため、以下のチェックは固定タグではなくイメージファミリーに一致します。

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->