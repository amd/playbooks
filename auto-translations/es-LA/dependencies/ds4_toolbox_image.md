<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Descargando la imagen del contenedor toolbox de ds4

`ds4-cockpit` ejecuta el motor de inferencia de ds4 dentro de un contenedor toolbox. En la pestaña **Interactive Toolboxes**, selecciona el toolbox disponible más reciente (por ejemplo, `ds4-rocm-7.2.4`) y haz clic en **Create/Update** para descargar la imagen.

Para descargar la imagen directamente en su lugar:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

La versión del toolbox cambia con el tiempo, por lo que la verificación a continuación coincide con la familia de la imagen en lugar de una etiqueta fija.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->