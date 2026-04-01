<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman is containerization software for Linux.


Step 1: Install the core Podman engine and the standalone Compose V2 parsing plugin

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin
```

Step 2: Enable the system-wide Podman API socket so the Compose plugin can communicate with the container runtime.

```bash
sudo systemctl enable --now podman.socket
```
Step 3: Run a temporary test container to verify the engine can successfully pull and execute images.

```bash
sudo podman run --rm docker.io/library/hello-world
```