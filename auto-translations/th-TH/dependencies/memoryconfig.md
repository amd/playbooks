<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @os:windows -->

<!-- @device:halo_box -->

สำหรับ Ryzen AI Halo หน่วยความจำ GPU เฉพาะจะถูกตั้งค่าเริ่มต้นไว้ที่ 64GB ซึ่งเพียงพอสำหรับปริมาณงานส่วนใหญ่ สำหรับโมเดลที่มีขนาดใหญ่ขึ้นหรือบริบทที่ยาวขึ้น การเพิ่มค่านี้อาจช่วยได้ หากต้องการปรับค่า ให้เปิด **AMD Software: Adrenalin Edition™** และไปที่ **Performance → Tuning → AMD Variable Graphics Memory** รีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

หากต้องการเปลี่ยนค่าหน่วยความจำ GPU เฉพาะ ให้เปิด **AMD Software: Adrenalin Edition™** และไปที่ **Performance → Tuning → AMD Variable Graphics Memory** รีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/adrenalin_vram_new.png" alt="AMD Software Adrenalin Edition — AMD Variable Graphics Memory panel" width="600"/>
</p>

<!-- @device:end -->

<!-- @os:end -->

<!-- @os:linux -->

บนระบบ Linux หากต้องการรันโมเดลที่มีขนาดใหญ่ขึ้น ให้เพิ่มพื้นที่ **หน่วยความจำที่ใช้ร่วมกัน (shared memory)** ที่พร้อมใช้งานสำหรับ GPU ซึ่งอาจต้องตั้งค่าหน่วยความจำ GPU เฉพาะใน BIOS ให้อยู่ในระดับต่ำสุด เพื่อให้พื้นที่หน่วยความจำที่ใช้ร่วมกันสามารถเพิ่มได้สูงสุด

<!-- @device:halo_box -->

สำหรับ AMD Ryzen™ AI Halo หากต้องการแก้ไขการตั้งค่าเริ่มต้น ให้เปิด **AMD Ryzen™ AI Developer Center** และไปที่แท็บ **Settings** ภายใต้ **Graphics Performance Settings** ให้เพิ่มค่าแถบเลื่อน **Shared Video Memory** จากนั้นคลิก **Apply Changes** และรีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<p align="center">
  <img src="/api/dependencies/assets/memory-config/linux_mem_new.png" alt="AMD Ryzen AI Developer Center — Graphics Performance Settings with Shared Video Memory slider" width="600"/>
</p>

<!-- @device:end -->

<!-- @device:halo,stx,krk -->

เพิ่มพื้นที่หน่วยความจำที่ใช้ร่วมกันโดยการเปลี่ยนการตั้งค่าเพจของ Translation Table Manager (TTM) ในเคอร์เนล AMD แนะนำให้ตั้งค่า VRAM เฉพาะขั้นต่ำใน BIOS (0.5 GB) เพื่อให้มีพื้นที่สูงสุดสำหรับใช้เป็นหน่วยความจำที่ใช้ร่วมกัน

1. ติดตั้งยูทิลิตี้ `pipx` และเพิ่มพาธสำหรับ wheel ที่ติดตั้งผ่าน pipx ไปยังพาธค้นหาของระบบ:

   ```bash
   sudo apt install pipx
   pipx ensurepath
   ```

2. ติดตั้ง wheel `amd-debug-tools` จาก PyPI:

   ```bash
   pipx install amd-debug-tools
   ```

3. ตรวจสอบการตั้งค่าหน่วยความจำที่ใช้ร่วมกันในปัจจุบัน:

   ```bash
   amd-ttm
   ```

4. เพิ่มการจัดสรรหน่วยความจำที่ใช้ร่วมกัน (หน่วยเป็น GB):

   ```bash
   amd-ttm --set <NUM>
   ```

5. รีบูตเครื่องเพื่อให้การเปลี่ยนแปลงมีผล

<!-- @device:end -->

<!-- @os:end -->