<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Podman

Podman היא תוכנת קונטיינריזציה עבור Linux.


**שלב 1**: התקינו את מנוע ה-Podman הבסיסי ואת תוסף ה-Compose V2 העצמאי.

```bash
sudo apt update && sudo apt install -y podman docker-compose-plugin podman-compose
```

**שלב 2**: אמתו את Podman ואת Compose

```bash
podman --version
podman-compose --version
```

**שלב 3**: הפעילו את שקע ה-API הגלובלי של Podman כך שתוסף ה-Compose יוכל לתקשר עם סביבת ההרצה של הקונטיינרים.

```bash
sudo systemctl enable --now podman.socket
```
**שלב 4**: הריצו קונטיינר בדיקה זמני כדי לוודא שהמנוע מסוגל למשוך ולהריץ תמונות בהצלחה.

```bash
sudo podman run --rm docker.io/library/hello-world
```