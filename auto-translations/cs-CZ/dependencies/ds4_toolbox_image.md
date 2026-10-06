<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stahování obrazu kontejneru nástroje ds4 toolbox

`ds4-cockpit` spouští inferenční jádro ds4 uvnitř kontejnerového toolboxu. Na kartě **Interactive Toolboxes** vyberte nejnovější dostupný toolbox (např. `ds4-rocm-7.2.4`) a kliknutím na **Create/Update** obraz stáhněte.

Chcete-li místo toho stáhnout obraz přímo:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Verze toolboxu se postupem času mění, takže níže uvedená kontrola odpovídá rodině obrazů, nikoli pevně danému tagu.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->