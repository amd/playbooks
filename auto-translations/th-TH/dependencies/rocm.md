<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

#### ROCm

**เพิ่มผู้ใช้ปัจจุบันเข้าไปในกลุ่ม render และ video** 
```bash
sudo usermod -a -G render,video $LOGNAME
```

**รีสตาร์ทระบบของคุณเพื่อให้การตั้งค่ามีผล**
```bash
sudo reboot
```

**ติดตั้ง ROCm ในสภาพแวดล้อมเสมือน (virtual environment) ที่สร้างขึ้น**
> **หมายเหตุ**: ตรวจสอบให้แน่ใจว่าสภาพแวดล้อมเสมือนเปิดใช้งานอยู่ก่อนดำเนินการต่อ

<!-- @device:halo_box,halo -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1151]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:stx -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1150]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:krk -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1152]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx7900xt -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1100]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

<!-- @device:rx9070xt,r9700 -->
<!-- @test:id=install-rocm timeout=300 setup=activate-venv -->
```bash
python -m pip install --index-url https://stable.repo.amd.com/rocm/whl-next/ "rocm[libraries,devel,device-gfx1201]==10.0.0"
```
<!-- @test:end -->
<!-- @device:end -->

หากต้องการความช่วยเหลือในการติดตั้งเพิ่มเติม โปรดดูที่ [ROCm 10.0.0 Documentation](https://rocm.docs.amd.com/en/latest/install/rocm.html)