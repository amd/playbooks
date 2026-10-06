<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### משיכת תמונת מכולת הכלים (toolbox) של ds4

`ds4-cockpit` מריץ את מנוע ההסקה (inference) של ds4 בתוך מכולת כלים (container toolbox). בלשונית **Interactive Toolboxes**, בחרו את מכולת הכלים העדכנית הזמינה (לדוגמה, `ds4-rocm-7.2.4`) ולחצו על **Create/Update** כדי למשוך את התמונה.

כדי למשוך את התמונה ישירות במקום זאת:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

גרסת מכולת הכלים משתנה עם הזמן, ולכן הבדיקה שלהלן תואמת את משפחת התמונה ולא תגית קבועה.

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->