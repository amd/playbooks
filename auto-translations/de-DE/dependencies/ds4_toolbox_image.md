<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Abrufen des ds4-Toolbox-Container-Images

`ds4-cockpit` führt die ds4-Inferenz-Engine innerhalb einer Container-Toolbox aus. Wählen Sie im Tab **Interactive Toolboxes** die neueste verfügbare Toolbox aus (z. B. `ds4-rocm-7.2.4`) und klicken Sie auf **Create/Update**, um das Image abzurufen.

Um das Image stattdessen direkt abzurufen:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Die Toolbox-Version ändert sich im Laufe der Zeit, daher prüft die folgende Überprüfung die Image-Familie und nicht ein festes Tag.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->