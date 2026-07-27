<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

A Podman egy konténerizációs szoftver Linuxhoz.

**1. lépés**: Telepítse a Podman alapmotort és az önálló Compose V2 elemzőbővítményt.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**2. lépés**: Ellenőrizze a Podmant és a Compose-t

```bash
podman --version
podman-compose --version
```

**3. lépés**: Engedélyezze a rendszerszintű Podman API socketet, hogy a Compose bővítmény kommunikálni tudjon a konténer futtatókörnyezettel.

```bash
sudo systemctl enable --now podman.socket
```
**4. lépés**: Futtasson egy ideiglenes tesztkonténert annak ellenőrzésére, hogy a motor sikeresen le tudja-e tölteni és futtatni a képfájlokat.

```bash
sudo podman run --rm docker.io/library/hello-world
```