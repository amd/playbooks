<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**เพิ่มผู้ใช้ปัจจุบันเข้าในกลุ่ม render และ video** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**รีสตาร์ทระบบเพื่อใช้การตั้งค่า**
```bash
sudo reboot
```

**ติดตั้ง ROCm ในสภาพแวดล้อมเสมือนที่สร้างขึ้น**
> **หมายเหตุ**: ตรวจสอบให้แน่ใจว่าสภาพแวดล้อมเสมือนเปิดใช้งานอยู่ก่อนดำเนินการต่อ

<!-- @device:halo,halo_box -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1151/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1150/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx1152/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx110X-all/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://repo.amd.com/rocm/whl/gfx120X-all/ "rocm[libraries,devel]"
```
<!-- @test:end -->
<!-- @device:end -->

สำหรับความช่วยเหลือในการติดตั้งเพิ่มเติม โปรดดูที่[ลิงก์นี้](https://rocm.docs.amd.com/en/7.13.0-preview/install/rocm.html)