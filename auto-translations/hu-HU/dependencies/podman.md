<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

A Podman egy Linux-alapú konténerizációs szoftver.


**1. lépés**: Telepítse az alapvető Podman motort és az önálló Compose V2 elemző bővítményt.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**2. lépés**: Ellenőrizze a Podman és a Compose működését.

```bash
podman --version
podman-compose --version
```

**3. lépés**: Engedélyezze a rendszerszintű Podman API socketet, hogy a Compose bővítmény kommunikálni tudjon a konténer futtatókörnyezettel.

```bash
sudo systemctl enable --now podman.socket
```
**4. lépés**: Futtasson egy ideiglenes tesztkonténert annak ellenőrzésére, hogy a motor sikeresen le tudja-e tölteni és végre tudja-e hajtani a képeket.

```bash
sudo podman run --rm docker.io/library/hello-world
```