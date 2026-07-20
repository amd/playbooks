<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman هو برنامج حاويات (containerization) مخصص لنظام Linux.


**الخطوة 1**: قم بتثبيت محرك Podman الأساسي وإضافة (plugin) تحليل Compose V2 المستقلة.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**الخطوة 2**: تحقق من Podman وCompose

```bash
podman --version
podman-compose --version
```

**الخطوة 3**: قم بتفعيل مقبس (socket) واجهة برمجة تطبيقات Podman على مستوى النظام بحيث تتمكن إضافة Compose من التواصل مع بيئة تشغيل الحاويات.

```bash
sudo systemctl enable --now podman.socket
```
**الخطوة 4**: قم بتشغيل حاوية اختبار مؤقتة للتحقق من قدرة المحرك على سحب الصور وتنفيذها بنجاح.

```bash
sudo podman run --rm docker.io/library/hello-world
```