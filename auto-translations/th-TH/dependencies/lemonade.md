<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### Lemonade

#### การติดตั้ง Lemonade

<!-- @os:windows -->
ดาวน์โหลดตัวติดตั้งเวอร์ชันล่าสุดจาก [lemonade-server.ai](https://github.com/lemonade-sdk/lemonade/releases/latest/download/lemonade.msi) และรันไฟล์ `.msi`

หลังการติดตั้ง:
- `lemonade` CLI จะถูกเพิ่มลงใน PATH ของระบบโดยอัตโนมัติ
- Lemonade server จะทำงานในพื้นหลังโดยอัตโนมัติ

คุณสามารถติดตั้งแบบ silent ผ่าน command line ได้เช่นกัน:
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

สำหรับ distribution อื่น ๆ หรือการติดตั้งจาก source โปรดดูที่ [ตัวเลือกการติดตั้งทั้งหมด](https://lemonade-server.ai/docs/guide/install/)
<!-- @os:end -->


#### การตรวจสอบการติดตั้ง Lemonade

เปิด terminal แล้วรัน:
```bash
lemonade --version
```

คุณควรเห็นผลลัพธ์ดังนี้:
```
lemonade version x.y.z
```

หากคุณเห็นหมายเลขเวอร์ชัน แสดงว่า Lemonade ติดตั้งถูกต้องและพร้อมใช้งาน

สำหรับการอ้างอิงอย่างรวดเร็ว ต่อไปนี้คือคำสั่ง Lemonade CLI ที่ใช้บ่อย:

| คำสั่ง | สิ่งที่คำสั่งทำ |
| --- | --- |
| `lemonade --help` | แสดงคำสั่งและ flag ทั้งหมดที่มี |
| `lemonade --version` | แสดงเวอร์ชัน Lemonade ที่ติดตั้งอยู่ |
| `lemonade status` | ยืนยันว่า Lemonade server กำลังทำงานและเข้าถึงได้หรือไม่ โดย API base URL ที่เข้ากันได้กับ OpenAI เริ่มต้นคือ `http://localhost:13305/api/v1` |
| `lemonade list` | แสดงรายการโมเดลที่พร้อมใช้งานสำหรับการตั้งค่า Lemonade ของคุณ |
| `lemonade pull <MODEL_NAME>` | ดาวน์โหลดโมเดลโดยไม่เปิดใช้งาน |
| `lemonade run <MODEL_NAME>` | ดาวน์โหลดโมเดลหากจำเป็น จากนั้นเริ่มต้นสำหรับการ inference/chat |
| `lemonade run <MODEL_NAME> --llamacpp rocm` | เริ่มต้นโมเดล llama.cpp ด้วย ROCm backend |
| `lemonade run <MODEL_NAME> --llamacpp vulkan` | เริ่มต้นโมเดล llama.cpp ด้วย Vulkan backend |
| `lemonade config` | แสดงค่าการกำหนดค่า Lemonade ปัจจุบัน |
| `lemonade config set llamacpp.backend=rocm` | ตั้งค่า llama.cpp backend เริ่มต้นเป็น ROCm |

สำหรับตัวเลือก Lemonade server ล่าสุดหรือการแก้ไขปัญหา โปรดดูที่ [เอกสาร Lemonade อย่างเป็นทางการ](https://lemonade-server.ai/docs/lemonade-cli/)