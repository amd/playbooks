<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## ข้อกำหนดเบื้องต้น

### Windows

| องค์ประกอบ | เวอร์ชัน | หมายเหตุ |
|-----------|---------|-------|
| **Node.js** | 22.16+ | ติดตั้งไว้ล่วงหน้าและพร้อมใช้งานใน PATH บน AMD Ryzen™ AI Halo Developer Platform; ต้องติดตั้งด้วยตนเองบนอุปกรณ์อื่นทั้งหมด |
| **Lemonade Server** | latest | กำลังทำงานที่ `http://localhost:13305/api/v1` |

### Linux

| องค์ประกอบ | เวอร์ชัน | หมายเหตุ |
|-----------|---------|-------|
| **Node.js** | 22.16+ | ติดตั้งไว้ล่วงหน้าและพร้อมใช้งานใน PATH บน AMD Ryzen™ AI Halo Developer Platform; ต้องติดตั้งด้วยตนเองบนอุปกรณ์อื่นทั้งหมด |
| **Lemonade Server** | latest | กำลังทำงานที่ `http://localhost:13305/api/v1` |


## Lemonade LLM

เซิร์ฟเวอร์ Lemonade ควรกำลังทำงานอยู่พร้อมกับโมเดลที่เหมาะสมกับอุปกรณ์ที่โหลดไว้ (ดูคำสั่ง `lemonade run` สำหรับอุปกรณ์ของคุณได้ที่ README):

| อุปกรณ์ | Endpoint | โมเดล |
|--------|----------|-------|
| AMD Ryzen™ AI Halo Developer Platform <br> AMD Ryzen™ AI Max+ | `http://localhost:13305/api/v1` | `gpt-oss-120b-mxfp-GGUF` |
| AMD Ryzen™ AI 300 HX <br> AMD Ryzen™ AI 300 <br> AMD Radeon™ 7000 Series Graphics <br> AMD Radeon™ 9000 Series Graphics | `http://localhost:13305/api/v1` | `gpt-oss-20b-mxfp4-GGUF` |