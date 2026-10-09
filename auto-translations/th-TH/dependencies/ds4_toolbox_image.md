<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดึงอิมเมจคอนเทนเนอร์ของ ds4 toolbox

`ds4-cockpit` จะรัน ds4 inference engine ภายในคอนเทนเนอร์ toolbox ในแท็บ **Interactive Toolboxes** ให้เลือก toolbox ล่าสุดที่มีให้ใช้งาน (เช่น `ds4-rocm-7.2.4`) แล้วคลิก **Create/Update** เพื่อดึงอิมเมจ

หากต้องการดึงอิมเมจโดยตรงแทน:

```bash
podman pull docker.io/kyuz0/strix-halo-ds4-toolbox:rocm-7.2.4
```

เวอร์ชันของ toolbox จะเปลี่ยนแปลงไปตามเวลา ดังนั้นการตรวจสอบด้านล่างนี้จะจับคู่กับกลุ่มอิมเมจ (image family) แทนที่จะเป็นแท็กที่ตายตัว

<!-- @os:linux -->
<!-- @test:id=ds4-toolbox-image-present-linux timeout=120 hidden=True -->
```bash
podman images --format '{{.Repository}}:{{.Tag}}' | grep -i 'strix-halo-ds4-toolbox'
```
<!-- @test:end -->
<!-- @os:end -->