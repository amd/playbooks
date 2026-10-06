<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Scaricamento dell'immagine container toolbox ds4

`ds4-cockpit` esegue il motore di inferenza ds4 all'interno di un container toolbox. Nella scheda **Interactive Toolboxes**, seleziona il toolbox più recente disponibile (ad es. `ds4-rocm-7.2.4`) e fai clic su **Create/Update** per scaricare l'immagine.

Per scaricare l'immagine direttamente invece:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

La versione del toolbox cambia nel tempo, quindi il controllo seguente verifica la corrispondenza con la famiglia dell'immagine piuttosto che con un tag fisso.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->