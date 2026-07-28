<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podmanは、Linux向けのコンテナ化ソフトウェアです。


**手順1**: コアとなるPodmanエンジンと、スタンドアロンのCompose V2解析プラグインをインストールします。

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**手順2**: PodmanとComposeを確認します

```bash
podman --version
podman-compose --version
```

**手順3**: Composeプラグインがコンテナランタイムと通信できるように、システム全体のPodman APIソケットを有効にします。

```bash
sudo systemctl enable --now podman.socket
```
**手順4**: 一時的なテストコンテナを実行し、エンジンがイメージを正常にプルして実行できることを確認します。

```bash
sudo podman run --rm docker.io/library/hello-world
```