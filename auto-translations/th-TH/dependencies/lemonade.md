<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### การติดตั้ง Lemonade

<!-- @os:windows -->
ดาวน์โหลดตัวติดตั้งเวอร์ชันล่าสุดจาก [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) แล้วรันไฟล์ `.msi`

หลังจากติดตั้งแล้ว:
- CLI `lemonade` จะถูกเพิ่มเข้าไปใน PATH ของระบบโดยอัตโนมัติ
- เซิร์ฟเวอร์ Lemonade จะทำงานในพื้นหลังโดยอัตโนมัติ

คุณสามารถติดตั้งแบบเงียบ (silently) ผ่านบรรทัดคำสั่งได้เช่นกัน:
```cmd
msiexec /i lemonade-server-minimal.msi /qn
```
<!-- @os:end -->

<!-- @os:linux -->
**Ubuntu:**
```bash
sudo add-apt-repository ppa:lemonade-team/stable
sudo apt install lemonade-server
```

**Arch Linux (AUR):**
```bash
yay -S lemonade-server
```

สำหรับดิสทริบิวชันอื่น ๆ หรือต้องการติดตั้งจากซอร์สโค้ด โปรดดู [ตัวเลือกการติดตั้งแบบเต็ม](https://lemonade-server.ai/docs/guide/install/)
<!-- @os:end -->


#### การตรวจสอบการติดตั้ง Lemonade

เปิดเทอร์มินัลแล้วรัน:
```bash
lemonade --version
```

คุณควรเห็นผลลัพธ์ประมาณนี้:
```
lemonade version x.y.z
```

หากคุณเห็นหมายเลขเวอร์ชัน แสดงว่า Lemonade ได้รับการติดตั้งอย่างถูกต้องและพร้อมใช้งาน

สำหรับการอ้างอิงอย่างรวดเร็ว นี่คือคำสั่ง Lemonade CLI ที่ใช้บ่อย:

| คำสั่ง | สิ่งที่คำสั่งนี้ทำ |
| --- | --- |
| `lemonade --help` | แสดงคำสั่งและแฟล็กทั้งหมดที่มี |
| `lemonade --version` | แสดงเวอร์ชันของ Lemonade ที่ติดตั้งอยู่ |
| `lemonade status` | ยืนยันว่าเซิร์ฟเวอร์ Lemonade กำลังทำงานและสามารถเข้าถึงได้หรือไม่ URL ฐานของ API ที่รองรับ OpenAI โดยค่าเริ่มต้นคือ `http://localhost:13305/api/v1` |
| `lemonade list` | แสดงรายการโมเดลที่มีให้ใช้งานสำหรับการตั้งค่า Lemonade ของคุณ |
| `lemonade pull <MODEL_NAME>` | ดาวน์โหลดโมเดลโดยไม่เปิดใช้งาน |
| `lemonade run <MODEL_NAME>` | ดาวน์โหลดโมเดลหากจำเป็น จากนั้นเริ่มต้นสำหรับการอนุมาน/แชท |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | เริ่มต้นโมเดล llama.cpp ด้วยแบ็กเอนด์ ROCm |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | เริ่มต้นโมเดล llama.cpp ด้วยแบ็กเอนด์ Vulkan |
| `lemonade config` | แสดงค่าการกำหนดค่าปัจจุบันของ Lemonade |
| `lemonade config set llamacpp.backend=rocm` | ตั้งค่าแบ็กเอนด์ llama.cpp เริ่มต้นเป็น ROCm |

สำหรับตัวเลือกเซิร์ฟเวอร์ Lemonade ล่าสุดหรือการแก้ไขปัญหา โปรดดูที่ [เอกสารทางการของ Lemonade](https://lemonade-server.ai/docs/lemonade-cli/)