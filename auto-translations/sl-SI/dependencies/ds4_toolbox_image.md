<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Prenos vsebnika toolbox ds4

`ds4-cockpit` zažene sklepalni mehanizem ds4 znotraj vsebnika toolbox. V zavihku **Interactive Toolboxes** izberite najnovejši razpoložljivi toolbox (npr. `ds4-rocm-7.2.4`) in kliknite **Create/Update**, da prenesete sliko.

Če želite sliko prenesti neposredno:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Različica toolbox-a se sčasoma spreminja, zato spodnje preverjanje ustreza družini slik, ne pa fiksni oznaki.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->