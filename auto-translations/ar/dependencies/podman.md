<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman هو برنامج لإدارة الحاويات على نظام Linux.

**الخطوة 1**: قم بتثبيت محرك Podman الأساسي وإضافة تحليل Compose V2 المستقلة.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**الخطوة 2**: تحقق من Podman و Compose

```bash
podman --version
podman-compose --version
```

**الخطوة 3**: قم بتفعيل مقبس Podman API على مستوى النظام حتى تتمكن إضافة Compose من التواصل مع وقت تشغيل الحاويات.

```bash
sudo systemctl enable --now podman.socket
```
**الخطوة 4**: قم بتشغيل حاوية اختبار مؤقتة للتحقق من أن المحرك يستطيع سحب الصور وتنفيذها بنجاح.

```bash
sudo podman run --rm docker.io/library/hello-world
```