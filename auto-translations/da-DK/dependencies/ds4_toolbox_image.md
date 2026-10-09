<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hentning af ds4-toolbox-containerimage

`ds4-cockpit` kører ds4-inferensmotoren inde i en container-toolbox. Vælg under fanen **Interactive Toolboxes** den nyeste tilgængelige toolbox (f.eks. `ds4-rocm-7.2.4`), og klik på **Create/Update** for at hente imaget.

Hvis du i stedet vil hente imaget direkte:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Toolbox-versionen ændrer sig over tid, så kontrollen nedenfor matcher imagefamilien frem for et fast tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->