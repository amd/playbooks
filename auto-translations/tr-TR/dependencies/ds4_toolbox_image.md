<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ds4 toolbox konteyner imajının çekilmesi

`ds4-cockpit`, ds4 çıkarım motorunu bir konteyner araç kutusu (toolbox) içinde çalıştırır. **Interactive Toolboxes** sekmesinde, mevcut en son araç kutusunu (ör. `ds4-rocm-7.2.4`) seçin ve imajı çekmek için **Create/Update** öğesine tıklayın.

İmajı doğrudan çekmek içinse:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Araç kutusu sürümü zaman içinde değiştiğinden, aşağıdaki kontrol sabit bir etiket yerine imaj ailesiyle eşleşir.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->