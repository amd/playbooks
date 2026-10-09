<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Henter container-avbildet for ds4-verktøykassen

`ds4-cockpit` kjører ds4-inferensmotoren inne i en verktøykasse i en container. Under fanen **Interactive Toolboxes** velger du den nyeste tilgjengelige verktøykassen (f.eks. `ds4-rocm-7.2.4`) og klikker på **Create/Update** for å hente avbildet.

For å hente avbildet direkte i stedet:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Verktøykasseversjonen endres over tid, så kontrollen nedenfor samsvarer med avbildfamilien i stedet for en fast tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->