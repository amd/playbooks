<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preuzimanje slike kontejnera ds4 toolbox

`ds4-cockpit` pokreće ds4 inference engine unutar container toolbox-a. U kartici **Interactive Toolboxes** izaberite najnoviji dostupni toolbox (npr. `ds4-rocm-7.2.4`) i kliknite **Create/Update** da biste preuzeli sliku.

Da biste sliku preuzeli direktno:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Verzija toolbox-a se vremenom menja, pa provera ispod odgovara porodici slike, a ne fiksnoj oznaci (tag).

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->