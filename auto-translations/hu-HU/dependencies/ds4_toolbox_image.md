<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### A ds4 toolbox konténerkép letöltése

A `ds4-cockpit` a ds4 következtető motort egy konténer eszköztáron (toolbox) belül futtatja. Az **Interactive Toolboxes** fülön válaszd ki a legújabb elérhető eszköztárat (pl. `ds4-rocm-7.2.4`), majd kattints a **Create/Update** gombra a kép letöltéséhez.

Ha inkább közvetlenül szeretnéd letölteni a képet:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Az eszköztár verziója időről időre változik, ezért az alábbi ellenőrzés a kép családjára illeszkedik, nem egy rögzített címkére (tag).

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->