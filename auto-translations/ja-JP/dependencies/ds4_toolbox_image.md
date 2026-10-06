<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4 toolboxコンテナイメージのプル

`ds4-cockpit`は、コンテナツールボックス内でds4推論エンジンを実行します。**Interactive Toolboxes**タブで、利用可能な最新のツールボックス(例: `ds4-rocm-7.2.4`)を選択し、**Create/Update**をクリックしてイメージをプルします。

代わりにイメージを直接プルするには:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

ツールボックスのバージョンは時間とともに変化するため、以下のチェックは固定のタグではなくイメージファミリーに一致します。

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->