<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Hämta containeravbildningen för ds4-verktygslådan

`ds4-cockpit` kör ds4-slutledningsmotorn inuti en container-verktygslåda. På fliken **Interactive Toolboxes** väljer du den senaste tillgängliga verktygslådan (t.ex. `ds4-rocm-7.2.4`) och klickar på **Create/Update** för att hämta avbildningen.

För att i stället hämta avbildningen direkt:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Verktygslådans version ändras över tid, så kontrollen nedan matchar avbildningsfamiljen i stället för en fast tagg.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->