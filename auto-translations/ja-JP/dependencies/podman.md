<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman は Linux 向けのコンテナ化ソフトウェアです。

**ステップ 1**: コアの Podman エンジンとスタンドアロンの Compose V2 パースプラグインをインストールします。

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**ステップ 2**: Podman と Compose を確認します。

```bash
podman --version
podman-compose --version
```

**ステップ 3**: Compose プラグインがコンテナランタイムと通信できるよう、システム全体の Podman API ソケットを有効にします。

```bash
sudo systemctl enable --now podman.socket
```
**ステップ 4**: エンジンがイメージを正常にプルして実行できることを確認するため、一時的なテストコンテナを実行します。

```bash
sudo podman run --rm docker.io/library/hello-world
```