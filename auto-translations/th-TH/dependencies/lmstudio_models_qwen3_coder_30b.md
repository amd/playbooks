<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### การดาวน์โหลด Qwen3-Coder 30B บน LM Studio

ในการดาวน์โหลดโมเดล Qwen3-Coder 30B:

1. กด "Ctrl" + "Shift" + "M" บนแป้นพิมพ์ของคุณ หรือคลิกที่แท็บ "Discover" (ไอคอนแว่นขยาย) บนแถบด้านข้างซ้าย
2. ค้นหา `Qwen3-Coder-30B-A3B`
3. เลือกระดับการควอนไทซ์ (แนะนำให้ใช้ `Q4_K_M` ซึ่งให้ความสมดุลที่ดีระหว่างขนาดและคุณภาพ) แล้วคลิก Download

LM Studio จะดาวน์โหลดและจัดวางโมเดลไว้ในไดเรกทอรีที่ถูกต้องให้โดยอัตโนมัติ

หากคุณต้องการดาวน์โหลดโมเดลเพิ่มเติม คุณสามารถค้นหาโมเดลเหล่านั้นได้ในแท็บ Discover และ LM Studio จะจัดการส่วนที่เหลือให้เอง

<!-- @os:windows -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-windows timeout=60 hidden=True -->
```powershell
lms ls --llm | Select-String -Pattern "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @test:id=lmstudio-model-present-qwen3-coder-linux timeout=60 hidden=True -->
```bash
lms ls --llm | grep -i "qwen3-coder-30b"
```
<!-- @test:end -->
<!-- @os:end -->