<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## Windows

### การติดตั้ง LM Studio

LM Studio ควรได้รับการติดตั้งไว้ล่วงหน้า:

| ส่วนประกอบ | เวอร์ชัน | ตำแหน่งที่ตั้ง |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### การดาวน์โหลดโมเดล

โมเดลต่อไปนี้ควรมีอยู่แล้วในไดเรกทอรีโมเดลของ LM Studio (`C:\Users\...\.lmstudio\models`):

| ประเภทโมเดล | การควอนไทซ์ | ขนาด | ตำแหน่งที่ตั้ง |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### การติดตั้ง LM Studio

ดูรายละเอียดเพิ่มเติมได้ที่ lmstudio.md (ในโฟลเดอร์ dependencies)

### การดาวน์โหลดโมเดล

เหมือนกับบน Windows