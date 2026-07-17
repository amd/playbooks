<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## ข้อกำหนดเบื้องต้น

### Windows

| ส่วนประกอบ | เวอร์ชัน | หมายเหตุ |
|-----------|---------|-------|
| **Node.js** | 22.16+ | ติดตั้งไว้ล่วงหน้าและพร้อมใช้งานใน PATH บน AMD Ryzen™ AI Halo Developer Platform; ต้องติดตั้งด้วยตนเองบนอุปกรณ์อื่นทั้งหมด |
| **Lemonade Server** | latest | กำลังทำงานบน `http://localhost:13305/api/v1` |

### Linux

| ส่วนประกอบ | เวอร์ชัน | หมายเหตุ |
|-----------|---------|-------|
| **Node.js** | 22.16+ | ติดตั้งไว้ล่วงหน้าและพร้อมใช้งานใน PATH บน AMD Ryzen™ AI Halo Developer Platform; ต้องติดตั้งด้วยตนเองบนอุปกรณ์อื่นทั้งหมด |
| **Lemonade Server** | latest | กำลังทำงานบน `http://localhost:13305/api/v1` |


## Lemonade LLM

เซิร์ฟเวอร์ Lemonade ควรทำงานโดยโหลดโมเดลที่เหมาะสมกับอุปกรณ์ (ดู README สำหรับคำสั่ง `lemonade run` ของอุปกรณ์คุณ):

| อุปกรณ์ | Endpoint | โมเดล |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |