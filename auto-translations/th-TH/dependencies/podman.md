<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman คือซอฟต์แวร์การจัดการคอนเทนเนอร์สำหรับ Linux

**ขั้นตอนที่ 1**: ติดตั้ง Podman engine หลักและปลั๊กอิน Compose V2 แบบ standalone สำหรับการแยกวิเคราะห์

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**ขั้นตอนที่ 2**: ตรวจสอบ Podman และ Compose

```bash
podman --version
podman-compose --version
```

**ขั้นตอนที่ 3**: เปิดใช้งาน Podman API socket ระดับระบบ เพื่อให้ปลั๊กอิน Compose สามารถสื่อสารกับ container runtime ได้

```bash
sudo systemctl enable --now podman.socket
```
**ขั้นตอนที่ 4**: รันคอนเทนเนอร์ทดสอบชั่วคราวเพื่อตรวจสอบว่า engine สามารถดึงและรันอิมเมจได้สำเร็จ

```bash
sudo podman run --rm docker.io/library/hello-world
```