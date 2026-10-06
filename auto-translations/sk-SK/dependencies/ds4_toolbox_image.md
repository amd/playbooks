<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Stiahnutie obrazu kontajnera toolbox ds4

`ds4-cockpit` spúšťa inferenčný engine ds4 vo vnútri kontajnera toolbox. Na karte **Interactive Toolboxes** vyberte najnovší dostupný toolbox (napr. `ds4-rocm-7.2.4`) a kliknutím na **Create/Update** stiahnete obraz.

Ak chcete obraz stiahnuť priamo:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Verzia toolboxu sa časom mení, preto nasledujúca kontrola zodpovedá rodine obrazov, nie pevne stanovenej značke (tag).

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->