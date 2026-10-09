<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Récupération de l'image du conteneur de la boîte à outils ds4

`ds4-cockpit` exécute le moteur d'inférence ds4 à l'intérieur d'une boîte à outils conteneurisée. Dans l'onglet **Interactive Toolboxes**, sélectionnez la boîte à outils la plus récente disponible (par exemple `ds4-rocm-7.2.4`) et cliquez sur **Create/Update** pour récupérer l'image.

Pour récupérer l'image directement à la place :

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

La version de la boîte à outils change avec le temps, c'est pourquoi la vérification ci-dessous correspond à la famille de l'image plutôt qu'à une étiquette fixe.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->