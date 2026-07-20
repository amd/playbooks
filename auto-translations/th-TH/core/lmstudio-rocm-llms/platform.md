<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## Windows

### การติดตั้ง LM Studio

ควรติดตั้ง LM Studio ไว้ล่วงหน้าแล้ว:

| ส่วนประกอบ | เวอร์ชัน | ตำแหน่งที่ตั้ง |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### การดาวน์โหลดโมเดล

โมเดลต่อไปนี้ควรมีอยู่แล้วในไดเรกทอรีโมเดลของ LM Studio (`C:\Users\...\.lmstudio\models`):

| อุปกรณ์ | ประเภทโมเดล | การควอนไทซ์ | ขนาด (GB) | ตำแหน่งที่ตั้ง |
| ----- |------------|--------------|------|----------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | OpenAI GPT-OSS 120B | `MXFP4` | 63.39 | `models\ggml-org` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | Qwen3.5 9B | `Q4_K_M` | 6.55 | `models\lmstudio-community` |

---

## Linux

### การติดตั้ง LM Studio

ดูรายละเอียดเพิ่มเติมได้ที่ [lmstudio.md](../../dependencies/lmstudio.md)

### การดาวน์โหลดโมเดล

เหมือนกับบน Windows