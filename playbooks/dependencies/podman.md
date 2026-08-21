<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Container Engine (Docker or Podman)

These steps use the `docker` command. It works whether you have Docker itself, or `podman-docker` (a wrapper that provides a `docker`-compatible command backed by the Podman engine).

> **Already have Docker?** Use it as-is — you do not need to install anything below, and you should not install Podman alongside it. The `docker` commands in this playbook will work directly.

If you don't have a container engine yet, install `podman-docker`. It pulls in the Podman engine automatically and adds the `docker` command that maps to it, so a single package gives you everything the playbook needs.

**Step 1**: Install `podman-docker` (engine + `docker` wrapper) and the Compose provider.

```bash
sudo apt update && sudo apt install -y podman-docker podman-compose
```

**Step 2**: Verify the `docker` command and Compose are available.

```bash
docker --version
docker compose version
```

**Step 3**: Enable the system-wide Podman API socket so Compose can communicate with the container runtime.

```bash
sudo systemctl enable --now podman.socket
```

**Step 4**: Run a temporary test container to verify the engine can pull and execute images.

```bash
docker run --rm docker.io/library/hello-world
```
