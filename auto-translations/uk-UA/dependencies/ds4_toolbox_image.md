<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Завантаження образу контейнера ds4 toolbox

`ds4-cockpit` запускає інференс-двигун ds4 всередині контейнерного toolbox. На вкладці **Interactive Toolboxes** виберіть останній доступний toolbox (наприклад, `ds4-rocm-7.2.4`) і натисніть **Create/Update**, щоб завантажити образ.

Щоб завантажити образ напряму:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Версія toolbox з часом змінюється, тому наведена нижче перевірка відповідає сімейству образу, а не фіксованому тегу.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->