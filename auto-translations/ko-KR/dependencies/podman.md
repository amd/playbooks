<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman는 Linux용 컨테이너화 소프트웨어입니다.


**1단계**: 핵심 Podman 엔진과 독립형 Compose V2 파싱 플러그인을 설치합니다.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**2단계**: Podman 및 Compose 확인

```bash
podman --version
podman-compose --version
```

**3단계**: Compose 플러그인이 컨테이너 런타임과 통신할 수 있도록 시스템 전체 Podman API 소켓을 활성화합니다.

```bash
sudo systemctl enable --now podman.socket
```
**4단계**: 임시 테스트 컨테이너를 실행하여 엔진이 이미지를 성공적으로 가져오고 실행할 수 있는지 확인합니다.

```bash
sudo podman run --rm docker.io/library/hello-world
```