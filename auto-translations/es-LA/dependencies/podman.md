<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman es un software de containerización para Linux.


**Paso 1**: Instala el motor principal de Podman y el complemento independiente de análisis de Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Paso 2**: Verifica Podman y Compose

```bash
podman --version
podman-compose --version
```

**Paso 3**: Habilita el socket API de Podman a nivel de sistema para que el complemento de Compose pueda comunicarse con el entorno de ejecución de contenedores.

```bash
sudo systemctl enable --now podman.socket
```
**Paso 4**: Ejecuta un contenedor de prueba temporal para verificar que el motor pueda descargar y ejecutar imágenes correctamente.

```bash
sudo podman run --rm docker.io/library/hello-world
```