<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Το Podman είναι λογισμικό containerization για Linux.


**Βήμα 1**: Εγκαταστήστε τον βασικό κινητήρα Podman και το αυτόνομο πρόσθετο ανάλυσης Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Βήμα 2**: Επαλήθευση Podman και Compose

```bash
podman --version
podman-compose --version
```

**Βήμα 3**: Ενεργοποιήστε το σύστημα-wide Podman API socket ώστε το πρόσθετο Compose να μπορεί να επικοινωνεί με το περιβάλλον εκτέλεσης container.

```bash
sudo systemctl enable --now podman.socket
```
**Βήμα 4**: Εκτελέστε ένα προσωρινό δοκιμαστικό container για να επαληθεύσετε ότι ο κινητήρας μπορεί να κατεβάσει και να εκτελέσει εικόνες επιτυχώς.

```bash
sudo podman run --rm docker.io/library/hello-world
```