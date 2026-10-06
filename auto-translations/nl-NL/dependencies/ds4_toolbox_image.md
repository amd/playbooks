<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Het ds4-toolboxcontainerimage ophalen

`ds4-cockpit` voert de ds4-inferentie-engine uit binnen een containertoolbox. Selecteer in het tabblad **Interactive Toolboxes** de nieuwste beschikbare toolbox (bijv. `ds4-rocm-7.2.4`) en klik op **Create/Update** om het image op te halen.

Om het image in plaats daarvan direct op te halen:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

De toolboxversie verandert na verloop van tijd, dus de onderstaande controle komt overeen met de imagefamilie in plaats van een vaste tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->