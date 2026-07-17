<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman, Linux için bir konteynerleştirme yazılımıdır.

**Adım 1**: Temel Podman motorunu ve bağımsız Compose V2 ayrıştırma eklentisini yükleyin.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**Adım 2**: Podman ve Compose'u doğrulayın

```bash
podman --version
podman-compose --version
```

**Adım 3**: Compose eklentisinin konteyner çalışma zamanıyla iletişim kurabilmesi için sistem genelinde Podman API soketini etkinleştirin.

```bash
sudo systemctl enable --now podman.socket
```
**Adım 4**: Motorun görüntüleri başarıyla çekip çalıştırabildiğini doğrulamak için geçici bir test konteyneri çalıştırın.

```bash
sudo podman run --rm docker.io/library/hello-world
```