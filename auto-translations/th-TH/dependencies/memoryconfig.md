<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

สำหรับ Ryzen AI Halo หน่วยความจำ GPU เฉพาะจะมีค่าเริ่มต้นที่ 64GB ซึ่งเพียงพอสำหรับงานส่วนใหญ่ สำหรับโมเดลขนาดใหญ่หรือบริบทที่ยาวขึ้น การเพิ่มเป็น 96GB อาจช่วยได้ ในการปรับ ให้เปิด **AMD Software: Adrenalin Edition™** และไปที่ **Performance → Tuning → AMD Variable Graphics Memory** จากนั้นรีบูตเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

ในการเปลี่ยนค่าหน่วยความจำ GPU เฉพาะ ให้เปิด **AMD Software: Adrenalin Edition™** และไปที่ **Performance → Tuning → AMD Variable Graphics Memory** จากนั้นรีบูตเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

บน Linux เพื่อรันโมเดลขนาดใหญ่ขึ้น ให้เพิ่มพูล **shared memory** ที่พร้อมใช้งานสำหรับ GPU ซึ่งอาจต้องตั้งค่าหน่วยความจำ GPU เฉพาะใน BIOS ให้น้อยที่สุด เพื่อให้พูล shared memory สามารถขยายได้สูงสุด

<!-- @device:halo_box -->

สำหรับ AMD Ryzen™ AI Halo ค่าเริ่มต้นคือ shared 96GB ในการปรับแต่ง ให้เปิด **AMD Ryzen™ AI Developer Center** และไปที่แท็บ **Settings** ภายใต้ **Graphics Performance Settings** ให้เพิ่มแถบเลื่อน **Shared Video Memory** จากนั้นคลิก **Apply Changes** และรีบูตเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

เพิ่มพูล shared memory โดยการเปลี่ยนการตั้งค่าเพจ Translation Table Manager (TTM) ของเคอร์เนล AMD แนะนำให้ตั้งค่า VRAM เฉพาะขั้นต่ำใน BIOS (0.5 GB) เพื่อให้มีหน่วยความจำสูงสุดที่พร้อมใช้งานเป็น shared memory

1. ติดตั้งยูทิลิตี `pipx` และเพิ่มพาธสำหรับ wheel ที่ติดตั้งโดย pipx ไปยัง system search path:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. ติดตั้ง wheel `amd-debug-tools` จาก PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. ตรวจสอบการตั้งค่า shared memory ปัจจุบัน:

   ```bash
   amd-ttm
   ```

4. เพิ่มการจัดสรร shared memory (หน่วยเป็น GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. รีบูตเพื่อให้การเปลี่ยนแปลงมีผล

<!-- @device:end -->

<!-- @os:end -->