<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

Povlačenje slike kontejnera ds4 toolbox

`ds4-cockpit` pokreće ds4 mašinu za zaključivanje unutar toolbox kontejnera. U kartici **Interactive Toolboxes**, izaberite najnoviji dostupni toolbox (npr. `ds4-rocm-7.2.4`) i kliknite na **Create/Update** da biste povukli sliku.

Da biste sliku povukli direktno:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Verzija toolbox-a se vremenom menja, pa provera ispod poredi porodicu slike, a ne fiksnu oznaku (tag).

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->