<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Το Podman είναι λογισμικό εικονοποίησης (containerization) για Linux.

**Βήμα 1**: Εγκαταστήστε τον πυρήνα του Podman engine και το αυτόνομο plugin ανάλυσης Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Βήμα 2**: Επαληθεύστε το Podman και το Compose

```bash
podman --version
podman-compose --version
```

**Βήμα 3**: Ενεργοποιήστε το socket API του Podman σε επίπεδο συστήματος ώστε το plugin Compose να μπορεί να επικοινωνεί με το container runtime.

```bash
sudo systemctl enable --now podman.socket
```
**Βήμα 4**: Εκτελέστε ένα προσωρινό δοκιμαστικό container για να επαληθεύσετε ότι ο μηχανισμός μπορεί να κατεβάσει (pull) και να εκτελέσει επιτυχώς images.

```bash
sudo podman run --rm docker.io/library/hello-world
```