<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos slike vsebnika z orodjarno ds4

`ds4-cockpit` zažene sklep ds4 znotraj vsebnika z orodjarno. V zavihku **Interactive Toolboxes** izberite najnovejšo razpoložljivo orodjarno (npr. `ds4-rocm-7.2.4`) in kliknite **Create/Update**, da prenesete sliko.

Če želite sliko prenesti neposredno:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Različica orodjarne se sčasoma spreminja, zato spodnje preverjanje ustreza družini slike in ne fiksni oznaki.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->