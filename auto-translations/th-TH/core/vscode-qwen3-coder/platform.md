<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## Windows

### การติดตั้ง LM Studio

ควรติดตั้ง LM Studio ไว้ล่วงหน้า:

| Component | Version | Location |
|-----------|---------|----------|
| **LM Studio (Models + Msc)** | v0.4.0 | `C:\Users\...\.lmstudio` |
| **LM Studio (Program)** | v0.4.0 | `C:\Program Files\LM Studio` |
| **LM Studio (Cache)** | v0.4.0 | `C:\Users\...\AppData\Roaming\LM Studio` |

### การดาวน์โหลดโมเดล

โมเดลต่อไปนี้ควรมีอยู่แล้วในไดเรกทอรีโมเดลของ LM Studio (`C:\Users\...\.lmstudio\models`):

| Model Type | Quantization | Size | Location |
|------------|--------------|------|----------|
| Qwen3 Coder 30B A3b Instruct | `Q4 K M` | 18.2 GB | `models\lmstudio-community` |

---

## Linux

### การติดตั้ง LM Studio

ดู lmstudio.md (ภายในโฟลเดอร์ dependencies) สำหรับรายละเอียดเพิ่มเติม

### การดาวน์โหลดโมเดล

เหมือนกับบน Windows