<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดว่าจะใช้สำหรับการรัน playbook นี้

## แอปพลิเคชัน/เฟรมเวิร์กที่จำเป็น

### Windows/Linux

- **Lemonade Server** ควรได้รับการติดตั้งตาม
  [คู่มือการติดตั้ง Lemonade](https://lemonade-server.ai/docs/guide/install/)
- **Node.js 22.12 หรือใหม่กว่า** และ `npm` ซึ่งใช้โดย CLI ของ `agent-canvas`
- **uv** ตัวจัดการแพ็กเกจ Python ที่ Agent Canvas ใช้ในการจัดการ
  สภาพแวดล้อมของ agent server ติดตั้งได้จาก
  [คู่มือการติดตั้ง uv](https://docs.astral.sh/uv/getting-started/installation/)

## โมเดลที่จำเป็น

### Windows/Linux

โมเดลต่อไปนี้ต้องพร้อมใช้งานสำหรับ Lemonade Server ก่อนที่จะเริ่ม
playbook

| ประเภทโมเดล | รหัสโมเดล | หมายเหตุ |
| --- | --- | --- |
| โมเดลแชท GGUF | `Qwen3.6-35B-A3B-GGUF` | ให้บริการโดย Lemonade Server ที่ `http://127.0.0.1:13305/api/v1` ใช้โมเดล GGUF ที่มีขนาดเล็กกว่าบนอุปกรณ์ที่มีหน่วยความจำน้อยกว่า 32 GB |

เริ่มต้นโมเดลด้วย:

```bash
lemonade config set llamacpp.backend=vulkan
lemonade config set ctx_size=65536
lemonade run "Qwen3.6-35B-A3B-GGUF"
```
