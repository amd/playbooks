<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

### ComfyUI

<!-- @os:windows -->

1. ดาวน์โหลดตัวติดตั้ง ComfyUI สำหรับ Windows เวอร์ชันล่าสุดจาก [download.comfy.org](https://download.comfy.org/windows/nsis/x64)
2. เลือกการตั้งค่าฮาร์ดแวร์ของคุณ: เลือก `AMD ROCm`
3. เลือกตำแหน่งที่ต้องการติดตั้ง ComfyUI: ใช้เส้นทางเริ่มต้นหรือโฟลเดอร์ที่คุณต้องการ
4. การตั้งค่าแอปพลิเคชันบนเดสก์ท็อป: เราแนะนำให้ยกเลิกการเลือก "Automatic Updates" เพื่อให้แน่ใจว่าคุณใช้งานเวอร์ชันที่แนะนำของแอปนี้
5. กด "Next" เพื่อเริ่มการติดตั้ง

<!-- @os:end -->

<!-- @os:linux -->
#### โคลน ComfyUI
```bash
git clone https://github.com/Comfy-Org/ComfyUI.git
```

#### (ไม่บังคับ) เช็คเอาต์เวอร์ชันที่ระบุ
```bash
git checkout v0.19.2
```

#### ติดตั้งข้อกำหนดของ ComfyUI

เมื่อเปิดใช้งาน Python virtual environment แล้ว ให้รัน:
```bash
cd ComfyUI
pip install -r requirements.txt
```

> **หมายเหตุ**: ดูข้อมูลเพิ่มเติมได้ที่ [ComfyUI GitHub](https://github.com/comfy-org/ComfyUI)

<!-- @os:end -->