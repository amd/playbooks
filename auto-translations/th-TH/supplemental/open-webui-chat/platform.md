<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# การกำหนดค่าแพลตฟอร์ม

เอกสารนี้อธิบายการกำหนดค่าแพลตฟอร์มที่คาดหวังสำหรับการรัน playbook นี้

## แอปพลิเคชัน/เฟรมเวิร์กที่จำเป็น

### Windows/Linux
ควรติดตั้ง Lemonade ล่วงหน้าจาก [ที่นี่](https://lemonade-server.ai/install_options.html)

- **Open WebUI** (แอปเว็บฝั่ง frontend)
- **Lemonade Server** (เซิร์ฟเวอร์โมเดลฝั่ง backend)

> Playbook นี้รัน **Lemonade** (Lemonade server/app) แบบ **native** ส่วน **Open WebUI** รันในรูปแบบ **container** บน Linux (ผ่าน Podman) และในรูปแบบ **Python package** บน Windows แพ็กเกจ `open-webui` บน PyPI รองรับ Python ≤ 3.12 เท่านั้น ดังนั้น container บน Linux จึงช่วยหลีกเลี่ยงการจัดการ Python เวอร์ชันเก่า

## โมเดล (ใน Lemonade)

ควรดาวน์โหลดโมเดลภายใน **Lemonade app** (โดยใช้ Model Manager ที่มีในตัว) หรือผ่านคำสั่งจัดการโมเดลของ Lemonade (`lemonade pull <model_name>`) Playbook นี้ถือว่าโมเดลที่แนะนำด้านล่างได้รับการดาวน์โหลดแล้วและปรากฏในรายการ endpoint ของโมเดล

ตรวจสอบความพร้อมใช้งานของโมเดล:
- เปิด: `http://localhost:13305/api/v1/models`
- โมเดลที่ดาวน์โหลดแล้วจะแสดงอยู่ภายใต้ `"data"`

### โมเดลที่แนะนำ

| ความสามารถ | Model ID | หมายเหตุ |
|---|----|-----|
| LLM (รับข้อความ → ส่งออกข้อความ) | `Qwen3-4B-Hybrid` (หรือที่คล้ายกัน) | โมเดล LLM ของ Lemonade ใดก็ได้สำหรับการสนทนา การเติมข้อความ การเขียนโค้ด หรือการให้เหตุผล |
| VLM (รับภาพ → ส่งออกข้อความ) | `Qwen3.5-4B-GGUF` (หรือโมเดลใดก็ได้ในหมวด **Vision**) | โมเดล multimodal/vision ใดก็ได้ที่รับภาพเป็นส่วนหนึ่งของ input |
| การสร้างภาพ (รับข้อความ → ส่งออกภาพ) | `SDXL-Turbo` (หรือโมเดลใดก็ได้ในหมวด **Image**) | โมเดล Stable Diffusion ใดก็ได้ที่สร้างภาพจาก text prompt |
| เสียง (รับเสียงพูด → ส่งออกข้อความ) | `Whisper-Large-v3` (หรือโมเดลใดก็ได้ในหมวด **Audio**) | โมเดล ASR ใดก็ได้ที่แปลงเสียงเป็นข้อความ |

<p align="center">
  <img src="assets/lemonade_model_manager.png" alt="Lemonade Model Manager" width="600"/>
</p>

## พอร์ตที่ใช้งาน

- **Lemonade Server:** `http://localhost:13305`
- **Open WebUI:** `http://localhost:8080`

หากพอร์ตเหล่านี้ถูกใช้งานอยู่แล้วในระบบของคุณ ให้เปลี่ยนพอร์ตเมื่อเริ่มต้นเซิร์ฟเวอร์