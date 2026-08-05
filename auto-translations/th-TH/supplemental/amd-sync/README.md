<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

<!-- auto-translated-disclaimer v2 -->
> [!WARNING]
> **การแปลด้วยเครื่อง.** หน้านี้ได้รับการแปลโดยอัตโนมัติจากภาษาอังกฤษ และยังไม่ได้รับการตรวจสอบโดยมนุษย์ อาจมีข้อผิดพลาด และคำแนะนำ คำสั่ง การดาวน์โหลด ความพร้อมใช้งานของผลิตภัณฑ์ หรือเนื้อหาอื่นๆ บางส่วนอาจแตกต่างกันไปตามภาษาหรือภูมิภาค ในกรณีที่มีความไม่สอดคล้องหรือความคลาดเคลื่อนใดๆ ให้ถือว่าเวอร์ชันภาษาอังกฤษต้นฉบับของ playbook เป็นฉบับที่มีผลบังคับใช้และมีอำนาจเหนือกว่า
<!-- auto-translated-disclaimer:end -->

<!-- @github-only -->
> [!IMPORTANT]
> This playbook uses special tags that GitHub cannot render. Please visit [amd.com/playbooks](https://amd.com/playbooks) to correctly preview this content.
<!-- @github-only:end -->

# การพัฒนาระยะไกลด้วย AMD Sync

## ภาพรวม

**AMD Sync** เปลี่ยนแล็ปท็อปของคุณให้เป็นห้องควบคุมระยะไกลสำหรับ AMD Ryzen™ AI Halo ข้ามขั้นตอนการตั้งค่า SSH คีย์ และ IDE ด้วยตนเอง — ติดตั้ง AMD Sync แล้วเข้าถึงเทอร์มินัลระยะไกล VS Code, JupyterLab และแดชบอร์ด GPU/CPU/หน่วยความจำแบบเรียลไทม์บน Ryzen AI Halo ได้ด้วยการคลิกเพียงครั้งเดียว

เครื่องท้องถิ่นของคุณยังคงคุ้นเคยเหมือนเดิม ทุกคำสั่ง โน้ตบุ๊ก และโมเดลจะทำงานบน Ryzen AI Halo

> **เคล็ดลับ**: หน้านี้จะมีการอัปเดตใหม่ ๆ ของ AMDSync

## สิ่งที่คุณจะได้เรียนรู้

- เปิดใช้งาน SSH บน Ryzen AI Halo และเชื่อมต่อไปยังเครื่องดังกล่าวจาก AMD Sync
- เปิด VS Code, Terminal, JupyterLab และ Live Metrics ที่เชื่อมกับ Ryzen AI Halo ได้ด้วยการคลิกเพียงครั้งเดียว
- จัดระเบียบงานระยะไกลโดยใช้โฟลเดอร์โปรเจกต์ที่จัดการโดย AMD Sync

---

## แนวคิดหลัก

AMD Sync มีสองฝั่ง: **client** (แล็ปท็อปของคุณ ที่รันแอป AMD Sync) และ **server** (Ryzen AI Halo ที่รันเซิร์ฟเวอร์ SSH ซึ่ง AMD Sync เจาะอุโมงค์เข้าไป) ทุกอย่างที่คุณเปิดจาก AMD Sync — VS Code, เทอร์มินัล, โน้ตบุ๊ก — จะเปิดขึ้นในเครื่องท้องถิ่น แต่ประมวลผลบน Ryzen AI Halo

> **ไคลเอนต์ที่รองรับ:** Windows 11 และ Linux ไม่รองรับ macOS

---

## ขั้นตอนที่ 1 — เปิดใช้งาน SSH บน Ryzen AI Halo


> **หมายเหตุ:** บน Windows, Ryzen AI Halo มาพร้อมกับเซิร์ฟเวอร์ SSH ที่ *ปิดใช้งานเป็นค่าเริ่มต้น* ส่วนบน Linux จะมาพร้อมกับเซิร์ฟเวอร์ SSH ที่ *เปิดใช้งานเป็นค่าเริ่มต้น*

1. บน Ryzen AI Halo เปิด **AMD Ryzen™ AI Developer Center**
2. ไปที่แท็บ **Remote**
3. เปิดสวิตช์ **SSH Server**
4. จดบันทึก **IP Address**, **Port** และ **Username** ที่แสดงอยู่ใต้ **Server Information** — คุณจะต้องนำไปวางใน AMD Sync

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/halobox_remote_tab.png" alt="AMD Ryzen AI Developer Center Remote tab showing SSH Server toggle and Server Information"/>
</div>

> **หมายเหตุ:** นี่คือ AMD Developer Center สำหรับ Windows ส่วนของ Linux อาจมี UI ที่แตกต่างกัน แต่มีฟังก์ชันการทำงานระยะไกลที่คล้ายคลึงกัน

> **เคล็ดลับ:** AMD Sync จะขอ **รหัสผ่านการเข้าสู่ระบบ OS** ของผู้ใช้นั้น ไม่ใช่รหัสผ่านจาก Developer Center

---

## ขั้นตอนที่ 2 — ติดตั้ง AMD Sync บนไคลเอนต์ของคุณ

AMD Sync ทำงานบน Windows 11 และ Linux ดาวน์โหลดตัวติดตั้งสำหรับระบบปฏิบัติการของคุณ จากนั้นทำตามขั้นตอนด้านล่าง หลังจากติดตั้งแล้ว คลิก **Accept & Install** ที่หน้าจอ **Get Started** — AMD Sync จะเปิดขึ้นโดยอัตโนมัติเมื่อเสร็จสิ้น

### Windows

[ดาวน์โหลด AMDSyncInstaller.exe](https://drivers.amd.com/drivers/amd-sync/windows/amdsyncinstaller.exe)

1. ดับเบิลคลิก `AMDSyncInstaller.exe`
2. คลิก **Accept & Install**

> หากมีการแจ้งเตือนจาก Windows Firewall ให้อนุญาตให้ AMD Sync เข้าถึงเครือข่ายเพื่อให้สามารถเชื่อมต่อกับ Ryzen AI Halo ผ่าน SSH ได้

### Linux

คลิกลิงก์เพื่อดาวน์โหลดในรูปแบบที่คุณต้องการ:

| รูปแบบ | ดาวน์โหลด | คำสั่งติดตั้ง |
|--------|----------|-----------------|
| `.deb` | [AMDSyncInstaller.deb](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.deb) | `sudo apt install ./amdsyncinstaller.deb` |
| `.rpm` | [AMDSyncInstaller.rpm](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.rpm) | `sudo rpm -i ./amdsyncinstaller.rpm` |
| `.AppImage` | [AMDSyncInstaller.AppImage](https://drivers.amd.com/drivers/amd-sync/linux/amdsyncinstaller.AppImage) | `chmod +x ./amdsyncinstaller.AppImage && ./amdsyncinstaller.AppImage` |

> **หมายเหตุ:** Ubuntu App Center อาจแจ้งเตือนไฟล์ `.deb` ที่เปิดในเครื่องว่า *"อาจไม่ปลอดภัย"* นี่เป็นคำเตือนมาตรฐานสำหรับตัวติดตั้งจากบุคคลที่สามในเครื่องใด ๆ หากการดับเบิลคลิกไฟล์ `.deb` ล้มเหลว ให้ใช้คำสั่งเทอร์มินัลด้านบนแทน

---

## ขั้นตอนที่ 3 — เชื่อมต่อกับ Ryzen AI Halo ของคุณ

เมื่อเปิดใช้งานครั้งแรก AMD Sync จะแสดงฟอร์ม **Add a Remote Device** กรอกข้อมูลโดยใช้ค่าจากแท็บ **Remote** ของ Developer Center

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/connect_device.png" alt="AMD Sync Add a Remote Device form"/>
</div>

| ฟิลด์ | หมายเหตุ |
|-------|-------|
| **Device Name** *(ไม่บังคับ)* | ป้ายชื่อที่จดจำง่าย เช่น `Ryzen AI Halo` ค่าเริ่มต้นคือ `Device 1`, `Device 2`, … |
| **Hostname or IP** | จากแท็บ Remote |
| **SSH Port** | จากแท็บ Remote (ตัวเลขเท่านั้น) |
| **Username** | ชื่อบัญชี OS ของคุณบน Ryzen AI Halo |
| **Password** | รหัสผ่านการเข้าสู่ระบบ OS ของคุณ — จะถูกซ่อนขณะพิมพ์ |

คลิก **Add Device** หลังจากหน้าจอโหลดสั้น ๆ คุณจะเห็นข้อความ **"Connection Successful"** และเข้าสู่หน้าหลัก ซึ่งจะอยู่ในถาดระบบของคุณ คลิกออกจากหน้าต่างเพื่อปิด AMD Sync จะยังคงทำงานอยู่และพร้อมใช้งานด้วยการคลิกเพียงครั้งเดียว

> **หากการเชื่อมต่อล้มเหลว** AMD Sync จะกลับไปที่ฟอร์มพร้อมค่าที่คุณกรอกไว้ สาเหตุทั่วไปได้แก่ SSH ถูกปิดใช้งานบน Ryzen AI Halo, รหัสผ่านไม่ถูกต้อง หรือทั้งสองเครื่องอยู่คนละเครือข่ายกัน

---

## ขั้นตอนที่ 4 — เปิดใช้เครื่องมือระยะไกลตัวแรกของคุณ

หน้าหลักมีคอมโพเนนต์แบบคลิกเดียวห้าตัว — ใช้งานได้ทั้งหมดไม่ว่าไคลเอนต์และ Ryzen AI Halo จะใช้ระบบปฏิบัติการใดก็ตาม

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/homepage_after_connect.png" alt="AMD Sync home view with Directory dropdown and launchers"/>
</div>

| คอมโพเนนต์ | สิ่งที่ทำ |
|-----------|--------------|
| **Directory** | เลือกโฟลเดอร์บน Ryzen AI Halo ที่ VS Code, Terminal และ JupyterLab จะเปิดขึ้น ค่าเริ่มต้นคือพื้นที่ทำงาน `Documents/AMD_Sync` ที่ถูกจัดการ |
| **VS Code** | เปิด VS Code ในเครื่องท้องถิ่นพร้อมอุโมงค์ SSH เข้าสู่โฟลเดอร์ที่เลือก |
| **Terminal** | เปิดเทอร์มินัลในเครื่องท้องถิ่นที่เชื่อมต่อ SSH กับ Ryzen AI Halo ในโฟลเดอร์ที่เลือก |
| **JupyterLab** | เปิดโปรเจกต์โน้ตบุ๊กที่เชื่อมต่อ SSH กับ Ryzen AI Halo โดยจำกัดขอบเขตอยู่ในโฟลเดอร์ที่เลือก |
| **Live Metrics** | มุมมองแบบเรียลไทม์ของการใช้งาน GPU, หน่วยความจำ และ CPU บน Ryzen AI Halo |

### ลองใช้ VS Code

สำหรับการเปิดใช้งานครั้งแรก ลองใช้ **VS Code**

1. ปล่อยให้ **Directory** เป็นค่าเริ่มต้น `~/Documents/AMD_Sync`
2. คลิก **VS Code**
3. AMD Sync จะสร้าง `Documents/AMD_Sync/Project_1` บน Ryzen AI Halo และเปิด VS Code ในเครื่องท้องถิ่น พร้อมเจาะอุโมงค์เข้าไปยังโฟลเดอร์ดังกล่าว

ตอนนี้คุณกำลังแก้ไขไฟล์ที่อยู่บน Ryzen AI Halo ด้วยการตั้งค่า VS Code ในเครื่องท้องถิ่นของคุณ สร้างไฟล์ `helloworld.py` เพิ่มโค้ด `print("hello world")` เปิดเทอร์มินัลในตัว (`` Ctrl + ` ``) แล้วรันไฟล์นั้น:

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/vscode.png" alt="VS Code SSH-tunneled into Project_1 on the Ryzen AI Halo, running helloworld.py"/>
</div>

แถบสถานะแสดงข้อความ **SSH: Linux** — เป็นการยืนยันว่าโค้ดของคุณกำลังทำงานบน Ryzen AI Halo ไม่ใช่บนแล็ปท็อปของคุณ
### ลองใช้งาน Terminal

คลิก **Terminal** เพื่อเข้าสู่โฟลเดอร์เดียวกันผ่าน SSH โดยไม่ต้องออกจากคีย์บอร์ด

<div align="center" style="max-width: 620px; margin: 1.5rem auto;">
  <img src="assets/terminal.png" alt="Local terminal SSH-connected to the Ryzen AI Halo in ~/Documents/AMD_Sync"/>
</div>

บน Windows เทอร์มินัลเริ่มต้นคือ **PowerShell** — สลับไปใช้ **Windows Command Prompt** ได้จากเมนู Settings หากคุณต้องการ ส่วนบน Linux นั้น AMD Sync จะใช้เทอร์มินัลเริ่มต้นของระบบของคุณ

---

## วิธีการทำงานของ Directory

ดรอปดาวน์ **Directory** คือตัวควบคุมที่สำคัญที่สุดเพียงหนึ่งเดียวใน AMD Sync — มันจะกำหนดว่าทุกเครื่องมือที่คุณเปิดใช้งานจะไปลงอยู่ที่ใดบน Ryzen AI Halo

- **`~/Documents/AMD_Sync` (ค่าเริ่มต้น)** — การเปิด VS Code หรือ JupyterLab จากที่นี่จะสร้างโฟลเดอร์โปรเจกต์ใหม่โดยอัตโนมัติ (`Project_1`, `Project_2`, … สำหรับ VS Code; `Notebook_Project_1`, `Notebook_Project_2`, … สำหรับ JupyterLab)
- **โฟลเดอร์โปรเจกต์ที่มีอยู่แล้ว** — โฟลเดอร์ลูกโดยตรงใด ๆ ของ `AMD_Sync` (รวมถึงโฟลเดอร์ที่คุณสร้างขึ้นเองบน Ryzen AI Halo) จะปรากฏในดรอปดาวน์ โฟลเดอร์ล่าสุดที่คุณใช้จะกลายเป็นค่าเริ่มต้นในครั้งถัดไป
- **เส้นทางที่กำหนดเอง** — พิมพ์เส้นทางแบบสัมบูรณ์ (absolute path) เพื่อเปิดโฟลเดอร์ในตำแหน่งอื่นบน Ryzen AI Halo AMD Sync จะทำการ *เปิด* เท่านั้น — จะไม่สร้างโฟลเดอร์นอก `AMD_Sync` และเส้นทางที่กำหนดเองจะไม่ถูกบันทึกไว้ระหว่างเซสชัน

หากเส้นทางที่กำหนดเองใช้งานไม่ได้ AMD Sync จะบอกเหตุผลให้คุณทราบ ไม่ว่าจะเป็นไวยากรณ์ไม่ถูกต้อง โฟลเดอร์ไม่มีอยู่จริง หรือเส้นทางนั้นชี้ไปยังไฟล์

---

## Live Metrics และ JupyterLab

- **Live Metrics** — แดชบอร์ดแบบเรียลไทม์แสดงการใช้งาน GPU หน่วยความจำ และ CPU เป็นวิธีที่เร็วที่สุดในการยืนยันว่าการฝึกโมเดลจากระยะไกลกำลังใช้งานฮาร์ดแวร์จริง
- **JupyterLab** — โปรเจกต์โน้ตบุ๊กแบบเต็มรูปแบบที่เชื่อมต่อผ่าน SSH ไปยัง Ryzen AI Halo พร้อมเทอร์มินัลในตัวสำหรับผสมผสานเซลล์โน้ตบุ๊กกับคำสั่งเชลล์โดยไม่ต้องออกจาก UI

---

## Settings และอุปกรณ์หลายเครื่อง

เมนู **Settings** มีสามแท็บ

| แท็บ | สิ่งที่ครอบคลุม |
|-----|----------------|
| **Devices** | แสดงรายการ Ryzen AI Halo ทุกเครื่องที่คุณเคยเชื่อมต่อสำเร็จ เชื่อมต่อใหม่ แก้ไขข้อมูลรับรอง หรือเพิ่มอุปกรณ์ใหม่ |
| **Information** | ลิงก์ไปยังเอกสารประกอบและฟอรัมสนับสนุน |
| **Customize** | ปรับตำแหน่งแอปบนเดสก์ท็อปของคุณ สลับประเภทเทอร์มินัล (เฉพาะ Windows) และตรวจสอบการอัปเดต AMD Sync |

<div align="center" style="max-width: 450px; margin: 1.5rem auto;">
  <img src="assets/customize_tab.png" alt="AMD Sync Settings menu Customize tab"/>
</div>


- **ประเภทเทอร์มินัล (Windows)** — เลือกระหว่าง **PowerShell** (ค่าเริ่มต้น) และ **Windows Command Prompt**
- **ประเภทเทอร์มินัล (Linux)** — มีเฉพาะเทอร์มินัลเริ่มต้นของระบบเท่านั้น
- **การอัปเดตแอป** — แท็บนี้เป็นจุดที่เหมาะสำหรับตรวจสอบและติดตั้ง AMD Sync เวอร์ชันใหม่จากภายใน UI ได้เลย ไม่จำเป็นต้องใช้ตัวอัปเดตแยกต่างหาก

> อุปกรณ์จะปรากฏใต้ **Devices** ก็ต่อเมื่อเชื่อมต่อสำเร็จเป็นครั้งแรกเท่านั้น ดังนั้นความพยายามที่ล้มเหลวจะไม่ทำให้รายการรก

---

## การแก้ไขปัญหา

- **การเชื่อมต่อล้มเหลวทันที** — ตรวจสอบว่าเปิดใช้งาน SSH server บนแท็บ **Remote** ใน Developer Center ของ Ryzen AI Halo แล้ว
- **ข้อผิดพลาดรหัสผ่านไม่ถูกต้อง** — ใช้ **รหัสผ่านสำหรับเข้าสู่ระบบปฏิบัติการ (OS login password)** บน Ryzen AI Halo ไม่ใช่รหัสผ่านที่นำมาจาก Developer Center
- **ปุ่ม VS Code ไม่มีปฏิกิริยาใด ๆ** — ติดตั้ง VS Code บนเครื่องไคลเอนต์ของคุณจาก [code.visualstudio.com](https://code.visualstudio.com)
- **ไอคอนถาดของ AMD Sync หายไป (Linux/GNOME)** — ติดตั้งและเปิดใช้งานส่วนขยาย AppIndicator
- **ไฟล์ `.deb` เปิดจากตัวจัดการไฟล์ไม่ได้** — ใช้คำสั่ง `sudo apt install ./AMDSyncInstaller.deb` จากเทอร์มินัล

---