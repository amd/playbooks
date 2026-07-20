<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman to oprogramowanie do konteneryzacji dla systemu Linux.


**Krok 1**: Zainstaluj podstawowy silnik Podman oraz samodzielną wtyczkę do parsowania Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Krok 2**: Zweryfikuj Podman i Compose

```bash
podman --version
podman-compose --version
```

**Krok 3**: Włącz ogólnosystemowe gniazdo API Podman, aby wtyczka Compose mogła komunikować się ze środowiskiem uruchomieniowym kontenerów.

```bash
sudo systemctl enable --now podman.socket
```
**Krok 4**: Uruchom tymczasowy kontener testowy, aby zweryfikować, czy silnik może pomyślnie pobierać i uruchamiać obrazy.

```bash
sudo podman run --rm docker.io/library/hello-world
```