<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman הוא תוכנת קונטיינריזציה עבור Linux.

**שלב 1**: התקן את מנוע Podman הבסיסי ואת תוסף הפענוח העצמאי Compose V2.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**שלב 2**: אמת את Podman ו-Compose

```bash
podman --version
podman-compose --version
```

**שלב 3**: הפעל את שקע ה-API של Podman ברמת המערכת כדי שתוסף ה-Compose יוכל לתקשר עם סביבת זמן הריצה של הקונטיינרים.

```bash
sudo systemctl enable --now podman.socket
```
**שלב 4**: הפעל קונטיינר בדיקה זמני כדי לאמת שהמנוע יכול למשוך ולהפעיל תמונות בהצלחה.

```bash
sudo podman run --rm docker.io/library/hello-world
```