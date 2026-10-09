<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### משיכת תמונת קונטיינר הארגז-כלים ds4

`ds4-cockpit` מריץ את מנוע ההסקה ds4 בתוך קונטיינר ארגז-כלים. בלשונית **Interactive Toolboxes**, בחרו את ארגז הכלים העדכני ביותר הזמין (למשל, `ds4-rocm-7.2.4`) ולחצו על **Create/Update** כדי למשוך את התמונה.

כדי למשוך את התמונה ישירות במקום זאת:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

גרסת ארגז הכלים משתנה עם הזמן, כך שהבדיקה שלהלן תואמת את משפחת התמונה ולא תגית קבועה.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->