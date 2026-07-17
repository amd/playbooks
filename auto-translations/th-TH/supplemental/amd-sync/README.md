<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# การพัฒนาระยะไกลด้วย AMD Sync

## ภาพรวม

**AMD Sync** เปลี่ยนแล็ปท็อปของคุณให้กลายเป็นศูนย์ควบคุมระยะไกลสำหรับ AMD Ryzen™ AI Halo ข้ามขั้นตอนการตั้งค่า SSH, คีย์, และ IDE ด้วยตนเอง — ติดตั้ง AMD Sync แล้วเข้าถึง terminal ระยะไกล, VS Code, JupyterLab และแดชบอร์ด GPU/CPU/หน่วยความจำแบบสดบน Ryzen AI Halo ได้ด้วยคลิกเดียว

เครื่องของคุณยังคงคุ้นเคยเหมือนเดิม ทุกคำสั่ง, โน้ตบุ๊ก และโมเดลทำงานบน Ryzen AI Halo

> **เคล็ดลับ**: หน้านี้จะมีการอัปเดตใหม่ๆ ของ AMDSync อยู่เสมอ

## สิ่งที่คุณจะได้เรียนรู้

- เปิดใช้งาน SSH บน Ryzen AI Halo และเชื่อมต่อจาก AMD Sync
- เปิด VS Code, Terminal, JupyterLab และ Live Metrics บน Ryzen AI Halo ด้วยคลิกเดียว
- จัดระเบียบงานระยะไกลโดยใช้โฟลเดอร์โปรเจกต์ที่จัดการโดย AMD Sync

---

## แนวคิดหลัก

AMD Sync มีสองฝั่ง: **ไคลเอนต์** (แล็ปท็อปของคุณ ที่รันแอป AMD Sync) และ **เซิร์ฟเวอร์** (Ryzen AI Halo ที่รัน SSH server ซึ่ง AMD Sync เชื่อมต่อผ่านอุโมงค์) ทุกสิ่งที่คุณเปิดจาก AMD Sync — VS Code, terminal, โน้ตบุ๊ก — จะเปิดบนเครื่องของคุณแต่ประมวลผลบน Ryzen AI Halo

> **ไคลเอนต์ที่รองรับ:** Windows 11 และ Linux ไม่รองรับ macOS

---

## ขั้นตอนที่ 1 — เปิดใช้งาน SSH บน Ryzen AI Halo


> **หมายเหตุ:** บน Windows, Ryzen AI Halo จะมาพร้อมกับ SSH server ที่ *ปิดอยู่โดยค่าเริ่มต้น* บน Linux จะมาพร้อมกับ SSH server ที่ *เปิดอยู่โดยค่าเริ่มต้น*

1. บน Ryzen AI Halo ให้เปิด **AMD Ryzen™ AI Developer Center**
2. ไปที่แท็บ **Remote**
3. สลับ **SSH Server** เป็นเปิด
4. จดบันทึก **IP Address**, **Port** และ **Username** ที่แสดงอยู่ใต้ **Server Information** — คุณจะต้องนำไปกรอกใน AMD Sync

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **หมายเหตุ:** นี่คือ AMD Developer Center สำหรับ Windows เวอร์ชัน Linux อาจมี UI ที่แตกต่างกัน แต่มีฟังก์ชันระยะไกลที่คล้ายกัน

> **เคล็ดลับ:** AMD Sync จะขอ **รหัสผ่านเข้าสู่ระบบ OS** ของผู้ใช้นั้น ไม่ใช่รหัสผ่านจาก Developer Center

---

## ขั้นตอนที่ 2 — ติดตั้ง AMD Sync บนไคลเอนต์ของคุณ

AMD Sync ทำงานบน Windows 11 และ Linux ดาวน์โหลดตัวติดตั้งสำหรับ OS ของคุณ แล้วทำตามขั้นตอนด้านล่าง หลังติดตั้ง ให้คลิก **Accept & Install** บนหน้าจอ **Get Started** — AMD Sync จะเปิดใช้งานโดยอัตโนมัติเมื่อเสร็จสิ้น

### Windows

[ดาวน์โหลด AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. ดับเบิลคลิก `AMDSyncInstaller.exe`
2. คลิก **Accept & Install**

> หาก Windows Firewall แจ้งเตือน ให้อนุญาตการเข้าถึงเครือข่ายของ AMD Sync เพื่อให้สามารถเชื่อมต่อกับ Ryzen AI Halo ผ่าน SSH ได้

### Linux

คลิกลิงก์เพื่อดาวน์โหลดรูปแบบที่คุณต้องการ:

| รูปแบบ | ดาวน์โหลด | คำสั่งติดตั้ง |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **หมายเหตุ:** Ubuntu App Center อาจแจ้งเตือนว่าไฟล์ `.deb` ที่เปิดในเครื่องเป็น *"อาจไม่ปลอดภัย"* นั่นเป็นคำเตือนมาตรฐานสำหรับตัวติดตั้งจากบุคคลที่สามในเครื่อง หากการดับเบิลคลิกไฟล์ `.deb` ล้มเหลว ให้ใช้คำสั่ง terminal ด้านบน

---

## ขั้นตอนที่ 3 — เชื่อมต่อกับ Ryzen AI Halo ของคุณ

เมื่อเปิดใช้งานครั้งแรก AMD Sync จะแสดงฟอร์ม **Add a Remote Device** กรอกข้อมูลโดยใช้ค่าจากแท็บ **Remote** ใน Developer Center

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| ฟิลด์ | หมายเหตุ |
|-------|-------|
| **Device Name** *(ไม่บังคับ)* | ชื่อที่จำง่าย เช่น `Ryzen AI Halo` ค่าเริ่มต้นคือ `Device 1`, `Device 2`, … |
| **Hostname or IP** | จากแท็บ Remote |
| **SSH Port** | จากแท็บ Remote (ตัวเลขเท่านั้น) |
| **Username** | ชื่อบัญชี OS ของคุณบน Ryzen AI Halo |
| **Password** | รหัสผ่านเข้าสู่ระบบ OS ของคุณ — แสดงเป็นจุดขณะพิมพ์ |

คลิก **Add Device** หลังจากหน้าจอโหลดสั้นๆ คุณจะเห็น **"Connection Successful"** และไปยังหน้าหลักซึ่งอยู่ใน system tray ของคุณ คลิกนอกหน้าต่างเพื่อปิด AMD Sync จะยังคงทำงานอยู่และเข้าถึงได้ด้วยคลิกเดียว

> **หากการเชื่อมต่อล้มเหลว** AMD Sync จะกลับไปที่ฟอร์มพร้อมค่าที่คุณกรอกไว้ สาเหตุที่พบบ่อยคือ SSH ถูกปิดใช้งานบน Ryzen AI Halo, รหัสผ่านผิด หรืออุปกรณ์ทั้งสองอยู่คนละเครือข่าย

---

## ขั้นตอนที่ 4 — เปิดใช้งานเครื่องมือระยะไกลครั้งแรก

หน้าหลักมีคอมโพเนนต์ห้าอย่างที่คลิกเดียวได้เลย — ทั้งหมดใช้งานได้ไม่ว่า OS ของไคลเอนต์และ Ryzen AI Halo จะเป็นอะไร

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| คอมโพเนนต์ | สิ่งที่ทำ |
|-----------|--------------|
| **Directory** | เลือกโฟลเดอร์บน Ryzen AI Halo ที่ VS Code, Terminal และ JupyterLab จะเปิดขึ้น ค่าเริ่มต้นคือพื้นที่ทำงาน `Documents/AMD_Sync` ที่จัดการโดย AMD Sync |
| **VS Code** | เปิด VS Code บนเครื่องของคุณพร้อม SSH tunnel เข้าสู่โฟลเดอร์ที่เลือก |
| **Terminal** | เปิด terminal บนเครื่องของคุณที่เชื่อมต่อ SSH กับ Ryzen AI Halo ในโฟลเดอร์ที่เลือก |
| **JupyterLab** | เปิดโปรเจกต์โน้ตบุ๊กที่เชื่อมต่อ SSH กับ Ryzen AI Halo ในขอบเขตของโฟลเดอร์ที่เลือก |
| **Live Metrics** | มุมมองแบบเรียลไทม์ของการใช้งาน GPU, หน่วยความจำ และ CPU บน Ryzen AI Halo |

### ลอง VS Code

สำหรับการเปิดใช้งานครั้งแรก ลอง **VS Code**

1. ปล่อย **Directory** ไว้ที่ค่าเริ่มต้น `~/Documents/AMD_Sync`
2. คลิก **VS Code**
3. AMD Sync จะสร้าง `Documents/AMD_Sync/Project_1` บน Ryzen AI Halo และเปิด VS Code บนเครื่องของคุณโดยเชื่อมต่อผ่านอุโมงค์เข้าสู่โฟลเดอร์นั้น

ตอนนี้คุณกำลังแก้ไขไฟล์ที่อยู่บน Ryzen AI Halo ด้วย VS Code บนเครื่องของคุณ สร้าง `helloworld.py`, เพิ่ม `print("hello world")`, เปิด integrated terminal (`` Ctrl + ` ``), แล้วรัน:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

แถบสถานะแสดง **SSH: Linux** — เป็นหลักฐานว่าโค้ดของคุณกำลังทำงานบน Ryzen AI Halo ไม่ใช่แล็ปท็อปของคุณ

### ลอง Terminal

คลิก **Terminal** เพื่อเข้าสู่โฟลเดอร์เดียวกันผ่าน SSH โดยไม่ต้องออกจากคีย์บอร์ด

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

บน Windows terminal เริ่มต้นคือ **PowerShell** — สลับไปใช้ **Windows Command Prompt** จากเมนู Settings หากต้องการ บน Linux AMD Sync จะใช้ terminal เริ่มต้นของระบบ

---

## วิธีการทำงานของ Directory

ดรอปดาวน์ **Directory** เป็นตัวควบคุมที่สำคัญที่สุดใน AMD Sync — มันกำหนดว่าทุกเครื่องมือที่คุณเปิดจะไปอยู่ที่ไหนบน Ryzen AI Halo

- **`~/Documents/AMD_Sync` (ค่าเริ่มต้น)** — การเปิด VS Code หรือ JupyterLab จากที่นี่จะสร้างโฟลเดอร์โปรเจกต์ใหม่โดยอัตโนมัติ (`Project_1`, `Project_2`, … สำหรับ VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … สำหรับ JupyterLab)
- **โฟลเดอร์โปรเจกต์ที่มีอยู่** — โฟลเดอร์ลูกโดยตรงของ `AMD_Sync` (รวมถึงโฟลเดอร์ที่คุณสร้างเองบน Ryzen AI Halo) จะปรากฏในดรอปดาวน์ โฟลเดอร์สุดท้ายที่คุณใช้จะกลายเป็นค่าเริ่มต้นในครั้งถัดไป
- **พาธที่กำหนดเอง** — พิมพ์พาธสัมบูรณ์ใดก็ได้เพื่อเปิดโฟลเดอร์ที่อื่นบน Ryzen AI Halo AMD Sync จะ *เปิด* เท่านั้น — จะไม่สร้างโฟลเดอร์นอก `AMD_Sync` และพาธที่กำหนดเองจะไม่ถูกบันทึกระหว่างเซสชัน

หากพาธที่กำหนดเองใช้งานไม่ได้ AMD Sync จะแจ้งสาเหตุ: ไวยากรณ์ไม่ถูกต้อง, โฟลเดอร์ไม่มีอยู่ หรือพาธชี้ไปที่ไฟล์

---

## Live Metrics และ JupyterLab

- **Live Metrics** — แดชบอร์ดสดของการใช้งาน GPU, หน่วยความจำ และ CPU วิธีที่เร็วที่สุดในการยืนยันว่าการฝึกโมเดลระยะไกลกำลังใช้งานฮาร์ดแวร์จริงๆ
- **JupyterLab** — โปรเจกต์โน้ตบุ๊กเต็มรูปแบบที่เชื่อมต่อ SSH กับ Ryzen AI Halo พร้อม integrated terminal สำหรับผสมเซลล์โน้ตบุ๊กและคำสั่ง shell โดยไม่ต้องออกจาก UI

---

## การตั้งค่าและอุปกรณ์หลายเครื่อง

เมนู **Settings** มีสามแท็บ:

| แท็บ | สิ่งที่ครอบคลุม |
|-----|----------------|
| **Devices** | แสดงรายการ Ryzen AI Halo ทุกเครื่องที่คุณเชื่อมต่อสำเร็จ เชื่อมต่อใหม่, แก้ไขข้อมูลรับรอง หรือเพิ่มอุปกรณ์ใหม่ |
| **Information** | ลิงก์ไปยังเอกสารและการสนับสนุนในฟอรัม |
| **Customize** | จัดตำแหน่งแอปบนเดสก์ท็อปของคุณ, สลับประเภท terminal (Windows เท่านั้น) และตรวจสอบการอัปเดต AMD Sync |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ประเภท terminal (Windows)** — เลือกระหว่าง **PowerShell** (ค่าเริ่มต้น) และ **Windows Command Prompt**
- **ประเภท terminal (Linux)** — มีเฉพาะ terminal เริ่มต้นของระบบเท่านั้น
- **การอัปเดตแอป** — แท็บนี้เป็นที่ที่เหมาะสมในการตรวจสอบและติดตั้งเวอร์ชัน AMD Sync ใหม่จากภายใน UI โดยไม่ต้องใช้ตัวอัปเดตแยกต่างหาก

> อุปกรณ์จะปรากฏใต้ **Devices** เฉพาะหลังจากการเชื่อมต่อครั้งแรกสำเร็จเท่านั้น ดังนั้นการพยายามเชื่อมต่อที่ล้มเหลวจะไม่ทำให้รายการรกรุงรัง

---

## การแก้ไขปัญหา

- **การเชื่อมต่อล้มเหลวทันที** — ยืนยันว่า SSH server เปิดใช้งานอยู่บนแท็บ **Remote** ของ Ryzen AI Halo ใน Developer Center
- **ข้อผิดพลาดรหัสผ่านผิด** — ใช้ **รหัสผ่านเข้าสู่ระบบ OS** บน Ryzen AI Halo ไม่ใช่รหัสผ่านจาก Developer Center
- **ปุ่ม VS Code ไม่ตอบสนอง** — ติดตั้ง VS Code บนเครื่องไคลเอนต์ของคุณจาก [code.visualstudio.com](https://code.visualstudio.com)
- **ไอคอน AMD Sync ใน tray หายไป (Linux/GNOME)** — ติดตั้งและเปิดใช้งานส่วนขยาย AppIndicator
- **`.deb` ไม่สามารถเปิดจาก file manager ได้** — ใช้ `sudo apt install ./AMDSyncInstaller.deb` จาก terminal

---