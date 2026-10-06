<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Récupération de l'image du conteneur toolbox ds4

`ds4-cockpit` exécute le moteur d'inférence ds4 dans un conteneur toolbox. Dans l'onglet **Interactive Toolboxes**, sélectionnez la dernière toolbox disponible (par exemple `ds4-rocm-7.2.4`) et cliquez sur **Create/Update** pour récupérer l'image.

Pour récupérer l'image directement à la place :

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

La version de la toolbox évolue avec le temps, c'est pourquoi la vérification ci-dessous correspond à la famille d'images plutôt qu'à un tag fixe.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->