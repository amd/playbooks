<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### LM Studio

<!-- @os:windows -->

<!-- @device:halo_box -->
สามารถติดตั้ง LM Studio ได้จาก **AMD Ryzen™ AI Developer Center** ไปที่แท็บ **Updates** แล้วติดตั้ง LM Studio หากยังไม่มีการติดตั้งไว้

หากระบบของคุณมีการติดตั้งโมเดลไว้ล่วงหน้า ให้ไปที่ Settings > General > Models Directory จากนั้นเปลี่ยนเส้นทางเป็น `C:\Users\Public\models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_windows_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

<!-- @device:halo,stx,krk,rx7900xt,rx9070xt,r9700 -->
1. ดาวน์โหลดตัวติดตั้งได้จากที่นี่: [https://lmstudio.ai/download](https://lmstudio.ai/download)
2. ติดตั้ง
<!-- @device:end -->

> **โมเดล:** หากระบบของคุณมาพร้อมกับโมเดลของ playbook นี้ที่ติดตั้งไว้ล่วงหน้าแล้ว ให้ชี้ LM Studio ไปยังไดเรกทอรีโมเดลที่ติดตั้งไว้ล่วงหน้าด้านบนเพื่อใช้งาน มิฉะนั้น ให้ดาวน์โหลดโมเดลจากแท็บ **Discover** ของ LM Studio (ไอคอนรูปแว่นขยาย) ก่อนดำเนินการต่อ

> เคล็ดลับ: หลังจากติดตั้งแล้ว ให้เปิด LM Studio หนึ่งครั้งเพื่อเริ่มต้นการทำงานของ CLI (`lms`)

<!-- @test:id=lmstudio-cli-windows timeout=60 hidden=True -->
```powershell
lms --help
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
> หมายเหตุ: คุณสามารถเลือกติดตั้งได้ทั้ง .deb หรือ AppImage
1. ดาวน์โหลด appimage ได้จากที่นี่: [https://lmstudio.ai/download?os=linux](https://lmstudio.ai/download?os=linux)
2. รันคำสั่ง `sudo apt install libfuse2`  
3. รันคำสั่ง `cd ~/Downloads`  
4. รันคำสั่ง `chmod +x LM-Studio-*.AppImage`  
5. รันคำสั่ง `./LM-Studio-*.AppImage`  
> เคล็ดลับ: หลังจากติดตั้งแล้ว ให้เปิด LM Studio หนึ่งครั้งเพื่อเริ่มต้นการทำงานของ CLI (`lms`)

<!-- @device:halo_box -->
หากระบบของคุณมีการติดตั้งโมเดลไว้ล่วงหน้า ให้ไปที่ Settings > General > Models Directory จากนั้นเปลี่ยนเส้นทางเป็น `/var/cache/models`

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_linux_directory.png" alt="Adding pre-installed models to LM Studio" width="600"/>
</p>
<!-- @device:end -->

> **โมเดล:** หากระบบของคุณมาพร้อมกับโมเดลของ playbook นี้ที่ติดตั้งไว้ล่วงหน้าแล้ว ให้ชี้ LM Studio ไปยังไดเรกทอรีโมเดลที่ติดตั้งไว้ล่วงหน้าด้านบนเพื่อใช้งาน มิฉะนั้น ให้ดาวน์โหลดโมเดลจากแท็บ **Discover** ของ LM Studio (ไอคอนรูปแว่นขยาย) ก่อนดำเนินการต่อ

<!-- @test:id=lmstudio-cli-linux timeout=60 hidden=True -->
```bash
lms --help
```
<!-- @test:end --> 
<!-- @os:end -->