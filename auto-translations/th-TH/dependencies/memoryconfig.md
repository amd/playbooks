<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

สำหรับ Ryzen AI Halo หน่วยความจำ GPU เฉพาะ (dedicated GPU memory) จะถูกตั้งค่าเริ่มต้นไว้ที่ 64GB ซึ่งเพียงพอสำหรับงานส่วนใหญ่ สำหรับโมเดลขนาดใหญ่หรือบริบทที่ยาวขึ้น การเพิ่มค่าเป็น 96GB อาจช่วยได้ หากต้องการปรับค่า ให้เปิด **AMD Software: Adrenalin Edition™** แล้วไปที่ **Performance → Tuning → AMD Variable Graphics Memory** จากนั้นรีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

หากต้องการเปลี่ยนค่าหน่วยความจำ GPU เฉพาะ (dedicated GPU memory) ให้เปิด **AMD Software: Adrenalin Edition™** แล้วไปที่ **Performance → Tuning → AMD Variable Graphics Memory** จากนั้นรีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

บน Linux หากต้องการรันโมเดลขนาดใหญ่ ให้เพิ่มพูล **shared memory** ที่ใช้งานได้กับ GPU ซึ่งอาจต้องตั้งค่าหน่วยความจำ GPU เฉพาะใน BIOS ให้อยู่ที่ค่าต่ำสุด เพื่อให้สามารถเพิ่มพูล shared memory ได้สูงสุด

<!-- @device:halo_box -->

สำหรับ AMD Ryzen™ AI Halo ค่าเริ่มต้นคือ 96GB แบบ shared หากต้องการปรับเปลี่ยนค่านี้ ให้เปิด **AMD Ryzen™ AI Developer Center** แล้วไปที่แท็บ **Settings** ภายใต้ **Graphics Performance Settings** ให้เพิ่มค่าตัวเลื่อน **Shared Video Memory** จากนั้นคลิก **Apply Changes** และรีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

เพิ่มพูล shared memory โดยการเปลี่ยนการตั้งค่า Translation Table Manager (TTM) page ของ kernel AMD แนะนำให้ตั้งค่า VRAM เฉพาะขั้นต่ำใน BIOS (0.5 GB) เพื่อให้ได้ปริมาณสูงสุดสำหรับใช้เป็น shared memory

1. ติดตั้งเครื่องมือ `pipx` และเพิ่มพาธสำหรับ wheel ที่ติดตั้งผ่าน pipx ลงในพาธค้นหาของระบบ:

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

4. เพิ่มปริมาณการจัดสรร shared memory (หน่วยเป็น GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. รีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<!-- @device:end -->

<!-- @os:end -->