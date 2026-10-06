<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Загрузка образа контейнера toolbox для ds4

`ds4-cockpit` запускает движок вывода ds4 внутри контейнера toolbox. На вкладке **Interactive Toolboxes** выберите последний доступный toolbox (например, `ds4-rocm-7.2.4`) и нажмите **Create/Update**, чтобы загрузить образ.

Чтобы загрузить образ напрямую:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

Версия toolbox со временем меняется, поэтому приведённая ниже проверка сопоставляется с семейством образа, а не с фиксированным тегом.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->