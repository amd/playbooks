<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Henter ds4 toolbox-containerimaget

`ds4-cockpit` kører ds4-inferensmotoren inde i en container toolbox. Under fanen **Interactive Toolboxes** skal du vælge den nyeste tilgængelige toolbox (f.eks. `ds4-rocm-7.2.4`) og klikke på **Create/Update** for at hente imaget.

For i stedet at hente imaget direkte:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Toolbox-versionen ændrer sig over tid, så tjekket nedenfor matcher imagefamilien frem for en fast tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->