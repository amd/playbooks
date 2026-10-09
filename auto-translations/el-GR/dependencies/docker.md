<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
Εγκαταστήστε το [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) και εκκινήστε το. Βεβαιωθείτε ότι η μηχανή του εκτελείται:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
Εγκαταστήστε το [Docker Engine](https://docs.docker.com/engine/install/ubuntu/), και στη συνέχεια προσθέστε τον χρήστη σας στην ομάδα `docker` ώστε το `docker` να εκτελείται χωρίς `sudo` (αποσυνδεθείτε και επανασυνδεθείτε στη συνέχεια). Βεβαιωθείτε ότι η μηχανή εκτελείται:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->