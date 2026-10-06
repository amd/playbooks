<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### سحب صورة حاوية ds4 toolbox

يقوم `ds4-cockpit` بتشغيل محرك الاستدلال ds4 داخل حاوية toolbox. في تبويب **Interactive Toolboxes**، اختر أحدث toolbox متاح (مثل `ds4-rocm-7.2.4`) وانقر على **Create/Update** لسحب الصورة.

لسحب الصورة مباشرة بدلاً من ذلك:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

يتغير إصدار toolbox بمرور الوقت، لذا فإن الفحص أدناه يطابق عائلة الصورة بدلاً من وسم (tag) ثابت.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->