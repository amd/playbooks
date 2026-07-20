<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด Qwen3.5 9B บน LM Studio

หากต้องการดาวน์โหลดโมเดล Qwen3.5 9B:

1. กด "Ctrl" + "Shift" + "M" บนแป้นพิมพ์ของคุณ หรือคลิกที่แท็บ "Discover" (ไอคอนแว่นขยาย) บนแถบด้านข้างซ้าย
2. ค้นหา `Qwen3.5 9B`
3. เลือกระดับการควอนไทซ์ (แนะนำให้ใช้ `Q4_K_M` ซึ่งให้ความสมดุลที่ดีระหว่างขนาดและคุณภาพ) แล้วคลิก Download

<p align="center">
  <img src="/api/dependencies/assets/lmstudio_download_qwen.png" alt="LM Studio Download Models" width="600"/>

LM Studio จะดาวน์โหลดและวางโมเดลไว้ในไดเรกทอรีที่ถูกต้องโดยอัตโนมัติ

หากคุณต้องการดาวน์โหลดโมเดลเพิ่มเติม คุณสามารถค้นหาได้ในแท็บ Discover และ LM Studio จะจัดการส่วนที่เหลือให้เอง

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3.5-9b"
```
<!-- @test:end -->
<!-- @os:end -->