<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Docker

<!-- @os:windows -->
ติดตั้ง [Docker Desktop for Windows](https://docs.docker.com/desktop/setup/install/windows-install/) แล้วเปิดใช้งาน ตรวจสอบว่าเอนจินของ Docker กำลังทำงานอยู่:

```powershell
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->

<!-- @os:linux -->
ติดตั้ง [Docker Engine](https://docs.docker.com/engine/install/ubuntu/) จากนั้นเพิ่มผู้ใช้ของคุณเข้าไปในกลุ่ม `docker` เพื่อให้สามารถรัน `docker` ได้โดยไม่ต้องใช้ `sudo` (ให้ออกจากระบบแล้วเข้าสู่ระบบใหม่หลังจากนั้น) ตรวจสอบว่าเอนจินกำลังทำงานอยู่:

```bash
sudo usermod -aG docker $USER
docker version --format '{{.Server.Version}}'
```
<!-- @os:end -->