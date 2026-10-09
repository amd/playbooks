<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Preluarea imaginii containerului toolbox ds4

`ds4-cockpit` rulează motorul de inferență ds4 într-un container toolbox. În fila **Interactive Toolboxes**, selectați cel mai recent toolbox disponibil (de ex. `ds4-rocm-7.2.4`) și faceți clic pe **Create/Update** pentru a prelua imaginea.

Pentru a prelua imaginea direct:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Versiunea toolbox-ului se schimbă în timp, așa că verificarea de mai jos se potrivește cu familia de imagini, nu cu o etichetă fixă.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->