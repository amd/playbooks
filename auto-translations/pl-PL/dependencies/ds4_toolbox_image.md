<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Pobieranie obrazu kontenera toolbox ds4

`ds4-cockpit` uruchamia silnik wnioskowania ds4 wewnątrz kontenera toolbox. Na karcie **Interactive Toolboxes** wybierz najnowszy dostępny toolbox (np. `ds4-rocm-7.2.4`) i kliknij **Create/Update**, aby pobrać obraz.

Aby pobrać obraz bezpośrednio:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Wersja toolbox zmienia się w czasie, dlatego poniższe sprawdzenie dopasowuje rodzinę obrazu, a nie stały tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->