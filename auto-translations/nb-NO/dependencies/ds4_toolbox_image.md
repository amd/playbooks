<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Henter ds4-toolbox-containeravbildningen

`ds4-cockpit` kjører ds4-inferensmotoren inne i en container-toolbox. Under fanen **Interactive Toolboxes** velger du den nyeste tilgjengelige toolboxen (f.eks. `ds4-rocm-7.2.4`) og klikker **Create/Update** for å hente avbildningen.

For i stedet å hente avbildningen direkte:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Toolbox-versjonen endrer seg over tid, så kontrollen under samsvarer med avbildningsfamilien snarere enn en fast tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->